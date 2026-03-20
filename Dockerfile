FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends cron curl procps && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fetch_hrrr.py /app/
COPY setup.py /app/

COPY start.sh /app/
RUN chmod +x /app/start.sh

COPY fetch_and_reload.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/fetch_and_reload.sh

COPY crontab.txt /etc/cron.d/hrrr-cron
RUN chmod 0644 /etc/cron.d/hrrr-cron
RUN crontab /etc/cron.d/hrrr-cron

RUN touch /var/log/cron.log

CMD ["/app/start.sh"]
