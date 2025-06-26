#!/bin/bash

crontab /app/crontab.txt

python -u /app/justwatcharr.py

exec cron -f