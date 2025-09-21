# Use an official lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (netcat-openbsd needed by wait-for-it.sh)
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy wait-for-it.sh into container and make it executable
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Expose FastAPI port
EXPOSE 8000

# Wait for Zookeeper and Kafka, then start FastAPI
CMD ["/wait-for-it.sh", "zookeeper:2181", "-t", "90", "--", "/wait-for-it.sh", "kafka:9092", "-t", "90", "--", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
