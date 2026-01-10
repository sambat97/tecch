FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

WORKDIR /app

# Install additional fonts
RUN apt-get update && apt-get install -y \
    fonts-noto-color-emoji \
    fonts-liberation2 \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright v1.48 ready')"

COPY . .

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

CMD ["python", "k12_bot.py"]
