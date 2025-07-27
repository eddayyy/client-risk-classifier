# 1. Base image: Python 3.12.3 slim
FROM python:3.12.3-slim

# 2. Set working directory
WORKDIR /app

# 3. Install any system dependencies you need
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy & install Python dependencies
COPY src/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copy application code
COPY src/ .

# 6. Expose your app port
EXPOSE 8000

# 7. Entrypoint
CMD ["python", "app.py"]
