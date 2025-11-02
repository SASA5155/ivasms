# Use official Python image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update && \
    apt-get install -y wget curl ca-certificates && \
    pip install --upgrade pip

# Copy files
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install

# Copy project code
COPY . .

# Command to run
CMD ["python", "ivasms_to_telegram.py"]
