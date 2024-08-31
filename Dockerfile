# Use an official Python runtime as a parent image
FROM python:3.12-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    curl \
    jq \
    libnss3 \
    libxss1 \
    libappindicator1 \
    fonts-liberation \
    xdg-utils \
    libu2f-udev \
    libgbm-dev \
    libasound2 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    libgbm1 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy ChromeDriver from local system to Docker container
COPY chromedriver-win32/chromedriver-win32/chromedriver.exe /usr/local/bin/chromedriver

# Copy Chrome binary if required, or specify its path if already installed on host

# Set environment variables for Chrome and ChromeDriver
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
ENV PATH="/usr/local/bin:$PATH"

# Install Selenium and other dependencies
RUN pip install selenium

# Copy the current directory contents into the container at /app
COPY . .

# Install any Python dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for Flask
EXPOSE 5000

# Define environment variable for Chrome to run headless
ENV DISPLAY=:99

# Run app.py when the container launches
CMD ["python", "app.py"]
