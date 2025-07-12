#!/bin/bash

case $RUNPERIOD in
	"Daily")
		cronstring="0 3 * * *"
		;;
	"Weekly")
		cronstring="0 3 * * 1"
		;;
	"Monthly")
		cronstring="0 3 1 * *"
		;;
	"Quarterly")
		cronstring="0 3 1 1,4,7,10 *"
		;;
	"Yearly")
		cronstring="0 3 1 1 *"
		;;
esac

echo "$cronstring /usr/local/bin/python /app/justwatcharr.py >> /var/log/cron.log 2>&1" > /etc/cron.d/justwatcharr
crontab /etc/cron.d/justwatcharr
touch /var/log/cron.log

/usr/local/bin/python /app/justwatcharr.py

cron && tail -f /var/log/cron.log
