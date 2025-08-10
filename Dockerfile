FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and clean up
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && pip install --no-cache-dir kafka-python==2.0.2 \
    && apt-get purge -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY consumer.py .

CMD ["python", "consumer.py"]
