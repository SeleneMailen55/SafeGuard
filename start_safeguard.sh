#!/bin/bash

echo "Starting SafeGuard..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

pip install -r requirements.txt

python app.py