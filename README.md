# 📦 Flipkart & Amazon Price Tracker 🛒  
Track prices of grocery products from Flipkart and Amazon and get instant alerts via Discord when prices drop!  
**Supports scheduled runs via GitHub Actions + Docker-ready** 🐳

---
## 🚀 Features

- ✅ Track prices from both **Amazon** & **Flipkart**
- 📉 Alerts when price drops below your target
- 🤖 Sends notifications to **Discord**
- 📅 Run on schedule with **GitHub Actions**
- 🐳 Lightweight Docker container support
- 🔐 Secure secrets using **environment variables**

---
## 🧪 Quick Start
```bash
git clone https://github.com/raviknox/price-tracker.git
cd price-tracker
python price_tracker.py --webhook $DISCORD_WEBHOOK_URL --config products.yaml --interval 1
```

---
## 🧾 Example `products.yaml`

```yaml
products:
  - name: "Product 1"
    flipkart_url: "https://www.flipkart.com/product-1-url"
    amazon_url: "https://www.amazon.in/product-1-url"
    target_price: 2000.00  # Set your target price
```

---
## 🐳 Docker Usage

### 🔧 Build locally:
```bash
docker build -t projectaccuknox/price-tracker:latest .
```

### ▶️ Run:
```bash
docker run --rm \
  -e DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..." \
  -v "$(pwd)/products.yaml:/tmp/products.yaml" \
  projectaccuknox/price-tracker:latest \
  --config "/tmp/products.yaml" \
  --interval 30
```

> 💡 Supports public URLs too!
> In this case we don't need to provide `-v "$(pwd)/products.yaml:/tmp/products.yaml"`
```bash
--config "https://raw.githubusercontent.com/raviknox/price-tracker/main/products.yaml"
```

---
## 🔐 Environment Variables

| Variable             | Required | Description                      |
|----------------------|----------|----------------------------------|
| `DISCORD_WEBHOOK_URL`| ✅       | Discord Webhook for notifications |

You can also pass the webhook using `--webhook` CLI flag, but `DISCORD_WEBHOOK_URL` is recommended for security.

---
## 🤖 GitHub Actions

### 📂 `.github/workflows/price-check.yml`

```yaml
name: 🔁 Price Tracker

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  run-tracker:
    runs-on: ubuntu-latest

    steps:
    - name: 📦 Pull Docker image
      run: docker pull projectaccuknox/price-tracker:latest

    - name: 🏃 Run Price Tracker
      run: |
        docker run --rm \
          -e DISCORD_WEBHOOK_URL=${{ secrets.DISCORD_WEBHOOK_URL }} \
          projectaccuknox/price-tracker:latest \
          --config "https://raw.githubusercontent.com/raviknox/price-tracker/main/products.yaml"
```

> 💬 Set your `DISCORD_WEBHOOK_URL` under:  
> **GitHub → Settings → Secrets → Actions**

---
## 📦 requirements.txt

```txt
requests
beautifulsoup4
schedule
PyYAML
```

---
## ❤️ Contribute

- Feel free to improve parsing selectors (they can change!)
- Add support for more stores
- Star this project if you found it useful 🌟

---
## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
