import os
import time
import schedule
import argparse
import requests
from bs4 import BeautifulSoup
import yaml

# Load products from YAML config
def load_config(filename):
    if filename.startswith("http://") or filename.startswith("https://"):
        try:
            print(f"🌍 Fetching config from URL: {filename}")
            response = requests.get(filename)
            if response.status_code == 200:
                return yaml.safe_load(response.text)
            else:
                print(f"❌ Error fetching remote config. HTTP Status: {response.status_code}")
        except Exception as e:
            print(f"Error loading config from URL: {e}")
    else:
        # Local file
        if os.path.exists(filename):
            print(f"📄 Loading local config from: {filename}")
            with open(filename, "r") as file:
                return yaml.safe_load(file)
        else:
            print(f"❌ Local config file not found: {filename}")
    return None

# Get Flipkart price
def get_flipkart_price(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        page = requests.get(url, headers=headers)
        if page.status_code != 200:
            print(f"❌ Failed to fetch Flipkart page. HTTP Status Code: {page.status_code}")
            return None

        soup = BeautifulSoup(page.content, "html.parser")
        
        # Look for the correct price div class "Nx9bqj CxhGGd"
        price_tag = soup.find("div", class_="Nx9bqj CxhGGd")
        
        if price_tag:
            price = price_tag.text.strip().replace("₹", "").replace(",", "")
            return float(price)
        else:
            print("⚠️ Could not find price on Flipkart page.")
            # Optional: print out the page content for debugging
            # print(soup.prettify())
    except Exception as e:
        print(f"Error fetching Flipkart price: {e}")
    return None

# Get Amazon price
def get_amazon_price(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        page = requests.get(url, headers=headers)
        if page.status_code != 200:
            print(f"❌ Failed to fetch Amazon page. HTTP Status Code: {page.status_code}")
            return None

        soup = BeautifulSoup(page.content, "html.parser")
        # print(soup.prettify())  # Debugging: print the entire page to find the price

        # Attempt to find the price using a different selector
        price_tag = soup.select_one("span.a-price .a-offscreen")
        if price_tag:
            price = price_tag.text.strip().replace("₹", "").replace(",", "")
            return float(price)
        else:
            print("⚠️ Could not find price on Amazon page.")
    except Exception as e:
        print(f"Error fetching Amazon price: {e}")
    return None

# Send message to Discord
def send_discord_alert(message, webhook_url):
    data = {"content": message}
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print("✅ Alert sent to Discord.")
        else:
            print(f"❌ Discord error: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error sending Discord alert: {e}")


# Compare each product
def check_all_prices(config_file, webhook_url):
    config = load_config(config_file)
    if not config:
        print("❌ Failed to load the config. Exiting...")
        return

    for product in config['products']:
        name = product['name']
        flipkart_price = get_flipkart_price(product['flipkart_url'])
        amazon_price = get_amazon_price(product['amazon_url'])
        target_price = product['target_price']

        # Initialize message
        message = f"📦 **{name}**\n"

        if flipkart_price:
            message += f"Flipkart: ₹{flipkart_price} "
        else:
            message += "⚠️ Flipkart price not found. "

        if amazon_price:
            message += f"| Amazon: ₹{amazon_price}\n"
        else:
            message += "| ⚠️ Amazon price not found.\n"

        if flipkart_price and amazon_price:
            if flipkart_price < amazon_price:
                message += "✅ Flipkart is cheaper.\n"
            elif amazon_price < flipkart_price:
                message += "✅ Amazon is cheaper.\n"
            else:
                message += "🤝 Prices are the same.\n"

        if flipkart_price and amazon_price and min(flipkart_price, amazon_price) <= target_price:
            message += f"🔔 **Dropped below ₹{target_price}!**\n"

        # Send message to Discord even if only one price is available
        send_discord_alert(message, webhook_url)


# === MAIN ===
if __name__ == "__main__":
    import os

    parser = argparse.ArgumentParser(description="📦 Price tracker for Flipkart & Amazon.")
    parser.add_argument("--config", type=str, default="products.yaml", help="Path or URL to the YAML config file")
    parser.add_argument("--webhook", type=str, help="Discord webhook URL (or set via DISCORD_WEBHOOK_URL env)")
    parser.add_argument("--interval", type=int, default=30, help="Check interval in minutes")

    args = parser.parse_args()

    # 🔐 Load webhook from ENV if not passed directly
    webhook_url = args.webhook or os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        raise ValueError("❌ Discord webhook URL not provided. Use --webhook or set DISCORD_WEBHOOK_URL env var.")

    # 🚀 Run once instantly
    print("🚀 Running initial price check...")
    config = load_config(args.config)

    if config:
        check_all_prices(args.config, webhook_url)

        # 🔁 Schedule future runs
        schedule.every(args.interval).minutes.do(check_all_prices, args.config, webhook_url)
        print(f"🔁 Tracker running every {args.interval} minutes... Press Ctrl+C to stop.")
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        print("❌ Could not load the config. Exiting...")
        exit(1)
