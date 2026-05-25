# Use an official Python runtime as a parent image
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    chromium chromium-driver \
    python3-dev && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port 8000
EXPOSE 8000

# Start the application using gunicorn by default
CMD ["gunicorn", "myweb.wsgi:application", "--bind", "0.0.0.0:8000"]
