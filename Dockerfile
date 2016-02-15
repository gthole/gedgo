FROM python:2.7

COPY ./ /src/

WORKDIR /src/
RUN pip install -r reqs.pip

RUN adduser --disabled-password --gecos '' gedgo
RUN chown -R gedgo:gedgo /src
USER gedgo
