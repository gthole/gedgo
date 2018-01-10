FROM python:2.7

COPY ./ /app/

WORKDIR /app/
RUN pip install -r reqs.pip
