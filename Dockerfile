# Use a newer Ubuntu base image that has GLIBC 2.38
FROM ubuntu:23.10

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    wget \
    build-essential \
    libnss3 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libcups2 \
    libdbus-1-3 \
    libxss1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Command to run the application
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]