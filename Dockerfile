FROM python:2.7

COPY ./ /app/

WORKDIR /app/
RUN pip install -r reqs.pip

RUN adduser --disabled-password --gecos '' gedgo
RUN chown -R gedgo:gedgo /app
USER gedgo
