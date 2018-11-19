FROM python:2.7-alpine3.7

WORKDIR /app/
COPY ./reqs.frozen.pip /app/
ENV LIBRARY_PATH=/lib:/usr/lib
RUN apk --update add jpeg-dev zlib-dev build-base mariadb-dev && \
    pip install -r reqs.frozen.pip && \
    apk add mariadb-client-libs && \
    apk del build-base mariadb-dev

COPY ./ /app/
RUN mkdir -p /static && python manage.py collectstatic -c --noinput
