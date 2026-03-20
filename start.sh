#!/bin/sh
# An entrypoint script for the hrrr-client service
# Fetches current HRRR forecast data and notifies hrrr-service to refresh

set -e

# Run the setup script to update zarr files
python3 /app/setup.py

# Tell running services to refresh
for ip in $(getent hosts tasks.hrrr-service | awk '{print $1}'); do
    curl -sS -X POST http://"$ip":8000/refresh >> /var/log/hrrr.log 2>&1 &
done
wait

# touch log file for cron job
touch /var/log/hrrr.log

# start cron
/usr/sbin/cron

# set foreground task to cron output
tail -f /var/log/hrrr.log