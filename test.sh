#!/bin/bash
set -e

rm -rf /app/files/test
mkdir /app/files/test

flake8 ./ --exclude migrations

python manage.py test gedgo
