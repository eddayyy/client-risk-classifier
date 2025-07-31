# 1. Base image: Python 3.12.3 slim
FROM python:3.12.3-slim

# 2. Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. Set working directory
WORKDIR /app

# 4. Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy & install Python dependencies
COPY src/requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copy application code
COPY src/ ./

# 7. Expose port (if serving an API)
EXPOSE 8000

# 8. Default command: train the model
#    To preprocess only, override with ["python", "modelmain.py", "preprocess"]
CMD ["python", "modelmain.py", "train"]