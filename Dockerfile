FROM ubuntu:latest
ADD . /srv/cache_school_data
WORKDIR /srv/cache_school_data
COPY ./dockerfiles/secrets.py ./cache_school_data/
COPY ./dockerfiles/cron-cache-school-data /etc/cron.d/
RUN apt-get update && \
    apt-get install --fix-missing -y python3 python3-dev python3-pip build-essential libpq-dev libffi-dev cron && \
    apt-get -y clean && \
    /usr/bin/pip3 install --upgrade pip && \
    /usr/bin/pip3 install boto3 zeep && \
    chmod 0644 /etc/cron.d/cron-cache-school-data
CMD ["cron", "-f"]
