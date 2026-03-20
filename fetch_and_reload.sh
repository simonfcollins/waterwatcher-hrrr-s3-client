#!/bin/sh
# Cron job to fetch most recent HRRR forecast data and signal hrrr-service refresh

set -e

# Fetch new zarrs
/usr/local/bin/python3 /app/fetch_hrrr.py >> /var/log/hrrr.log 2>&1

# Tell running services to refresh
for ip in $(getent hosts tasks.hrrr-service | awk '{print $1}'); do
    curl -sS -X POST http://"$ip":8000/refresh >> /var/log/hrrr.log 2>&1 &
done
wait
echo "$(date) - All HRRR-service replicas refreshed" >> /var/log/hrrr.log