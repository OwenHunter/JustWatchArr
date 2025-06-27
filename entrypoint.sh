#!/bin/bash

/usr/local/bin/python /app/justwatcharr.py
cron && tail -f /var/log/cron.log