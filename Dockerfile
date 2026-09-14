FROM python:3.13-slim

# Chromium и драйвер к нему из репозиториев Debian — версии заведомо совместимы,
# в отличие от связки "свежий Chrome + отдельно скачанный chromedriver"
RUN apt-get update && apt-get install -y --no-install-recommends \
        chromium \
        chromium-driver \
        fonts-liberation \
        curl \
        default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# Allure CLI — генерация HTML-отчёта внутри контейнера
RUN curl -fsSL -o /tmp/allure.tgz \
    https://github.com/allure-framework/allure2/releases/download/2.27.0/allure-2.27.0.tgz && \
    tar -zxf /tmp/allure.tgz -C /opt/ && \
    ln -s /opt/allure-2.27.0/bin/allure /usr/bin/allure && \
    rm /tmp/allure.tgz

ENV PATH="/usr/lib/chromium:${PATH}" \
    HEADLESS=true

WORKDIR /app

# Зависимости — отдельный слой, кэшируется пока requirements.txt не изменился
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["pytest", "-v", "--alluredir=allure-results"]
