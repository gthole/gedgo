FROM python:2.7

COPY ./ /app/

WORKDIR /app/
RUN pip install -r reqs.frozen.pip
RUN mkdir -p /static && python manage.py collectstatic -c --noinput

RUN adduser --disabled-password --gecos '' gedgo
RUN chown -R gedgo:gedgo /app
USER gedgo
