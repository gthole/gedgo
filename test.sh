#!/bin/bash
set -e

rm -rf /src/files/test
mkdir /src/files/test

flake8 ./ --exclude migrations

python manage.py test gedgo
