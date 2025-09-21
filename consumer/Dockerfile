# Base image
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Java and g++ for code execution
RUN apt-get update && apt-get install -y default-jdk g++ && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["python3", "python-consumer.py"]
