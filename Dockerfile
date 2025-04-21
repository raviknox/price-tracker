# ✅ Base image
FROM python:3.9-slim

# 🛠 Set working directory
WORKDIR /app

# 📦 Copy requirements first for caching
COPY requirements.txt .

# 🧰 Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 📄 Copy application files
COPY price_tracker.py .
COPY products.yaml .

# ✅ Set entrypoint and allow passing CLI args
ENTRYPOINT ["python", "price_tracker.py"]

# 🧪 Default CMD can be overridden. This avoids accidental errors.
CMD ["--help"]
