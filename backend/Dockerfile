# syntax=docker/dockerfile:1.4
FROM python:3.11-alpine
LABEL authors="Jan Kamburg"

# Install Nginx
RUN apk update && apk add nginx

COPY .docker/nginx.conf  /etc/nginx/http.d/totum.conf
RUN ln -sf /dev/stdout /var/log/nginx/access.log && ln -sf /dev/stderr /var/log/nginx/error.log


COPY ./ totum
WORKDIR /totum
RUN python -m venv .venv
RUN . /totum/.venv/bin/activate && pip3 install --upgrade pip
RUN . /totum/.venv/bin/activate && pip3 install -r requirements.txt --no-cache-dir
RUN . /totum/.venv/bin/activate && pip3 install gunicorn

RUN chmod +x .docker/start-server.sh

ENV TOTUM_SETTINGS_MODULE='Totum.config.settings.prod'
CMD ["/totum/.docker/start-server.sh"]