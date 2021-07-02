FROM python:3.7-alpine3.7

WORKDIR /app/
COPY ./reqs.pip /app/
ENV LIBRARY_PATH=/lib:/usr/lib
RUN apk --update add jpeg-dev zlib-dev build-base && \
    pip install -r reqs.pip && \
    apk del build-base

# Create a non-root user
RUN addgroup -S appgroup && adduser -S app -G appgroup

COPY ./ /app/
RUN mkdir -p /static && \
    chown app /static /app && \
    python manage.py collectstatic -c --noinput

USER app

CMD sh ./run.sh
