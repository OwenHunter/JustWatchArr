FROM python:3.13-slim

WORKDIR /app

COPY justwatcharr.py .
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y cron && apt-get clean

RUN echo "0 3 * * * /usr/local/bin/python /app/justwatcharr.py >> /var/log/cron.log 2>&1" > /etc/cron.d/justwatcharr
RUN crontab /etc/cron.d/justwatcharr
RUN touch /var/log/cron.log

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]