FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (if any needed for numpy/pandas)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn for production serving
RUN pip install gunicorn

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 5001

# Command to run the application using gunicorn
# 1 worker, 4 threads is a good starting point for free tier
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "1", "--threads", "4", "main:app"]