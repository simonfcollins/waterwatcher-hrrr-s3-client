#!/bin/sh

# Run the setup script to update zarr files
python3 /app/setup.py
# touch log file for cron job
touch /var/log/hrrr.log
# start cron
/usr/sbin/cron
# set foreground task to cron output
tail -f /var/log/hrrr.log