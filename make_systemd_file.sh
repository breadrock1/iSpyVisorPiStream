#!/bin/bash

APP_DIR=$(readlink -f $(dirname "$0"))    # where this script lives
PYTHON_DIR=$(dirname "$(which python)")   # where Python executable lives
THREADS=5
TIMEOUT=30
USER_=$USER

echo "[Unit]
Description=Gunicorn daemon for flaskcam
After=network.target

[Service]
User=$USER_
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$PYTHON_DIR"
ExecStart=$PYTHON_DIR/gunicorn --timeout $TIMEOUT --workers 1 --threads $THREADS --bind unix:flaskcam.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/flaskcam.service > /dev/null
