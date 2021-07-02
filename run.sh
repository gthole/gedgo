# /bin/sh
set -e

# Apply any migrations before launching the listener
./manage.py migrate

# Run the application
uvicorn --host=0.0.0.0 --workers=4 asgi:application
