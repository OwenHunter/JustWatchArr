FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY justwatcharr.py .
COPY requirements.txt .

RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
