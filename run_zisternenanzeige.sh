#!/bin/bash
cd "$(dirname "$0")"
set -e
filename="log_zisternenanzeige.log"
if [ -e "$filename" ]; then
    datestr="$(date -r $filename +%Y%m%d_%H%M%S)"
    mv "$filename" "logs/log_$new_filename.log"
fi
source ".venv/bin/activate"
python -u main.py
