# Using Ubuntu 22.04 LTS (Jammy)
FROM ubuntu:22.04


ENV DEBIAN_FRONTEND=noninteractive


WORKDIR /app


RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
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
    libxtst6 \
    xvfb \
    libgconf-2-4 \
    libatk1.0-0 \
    libdrm2 \
    libxkbcommon0 \
    fonts-liberation \
    libu2f-udev \
    libvulkan1 \
    && rm -rf /var/lib/apt/lists/*


RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"


COPY requirements.txt .


RUN pip3 install --no-cache-dir -r requirements.txt

RUN playwright install chromium
RUN playwright install-deps


COPY . .


EXPOSE 8080


CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]