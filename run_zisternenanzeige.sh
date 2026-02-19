#!/bin/bash
set -e
filename="log_zisternenanzeige.log"
if [ -e "$file" ]; then
    new_filename="$(date -r $filename +%Y%m%d_%H%M%S)"
    mv $filename $new_filename
fi
source "./Zisternenanzeige/.venv/bin/activate"
python -u Zisternenanzeige/main.py
