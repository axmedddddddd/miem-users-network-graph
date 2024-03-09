FROM python:3.10

RUN apt-get update && apt-get install -y cron

WORKDIR /code

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY graphmaker ./graphmaker

COPY crontab /etc/cron.d/graph-cron
RUN chmod 0644 /etc/cron.d/graph-cron

RUN crontab /etc/cron.d/graph-cron

RUN touch /var/log/cron.log

CMD cron && tail -f /var/log/cron.log
