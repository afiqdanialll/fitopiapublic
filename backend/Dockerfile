FROM python:alpine3.19

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
ADD ./backend /app/backend/

# Install system dependencies
RUN apk add --no-cache gcc musl-dev mariadb-connector-c-dev mariadb-dev wget chromium chromium-chromedriver

# Ensure Chromium and ChromeDriver are accessible
RUN [ ! -e /usr/bin/chromium-browser ] && ln -s /usr/lib/chromium/chromium /usr/bin/chromium-browser || true
RUN [ ! -e /usr/bin/chromedriver ] && ln -s /usr/lib/chromium/chromedriver /usr/bin/chromedriver || true

# Install Python dependencies
RUN pip install --upgrade pip && pip install gunicorn && pip install -r backend/requirements.txt

# Set PATH to include Chromedriver
ENV PATH="/usr/lib/chromium:/app/backend:${PATH}"