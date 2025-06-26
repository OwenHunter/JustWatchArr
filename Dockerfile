FROM python:3.13-slim

WORKDIR /app

COPY justwatcharr.py .
COPY crontab.txt .
COPY entrypoint.sh .
COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y cron && apt-get clean

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]