#!/bin/bash
cd "$(dirname "$0")"
set -e
filename="log_zisternenanzeige.log"
if [ -e "$file" ]; then
    new_filename="$(date -r $filename +%Y%m%d_%H%M%S)"
    mv $filename $new_filename
fi
source ".venv/bin/activate"
python -u main.py
