#!/bin/bash
cd "$(dirname "$0")"
set -e
filename="logs/latest.log"
if [ -e "$filename" ]; then
    datestr="$(date -r $filename +%Y%m%d_%H%M%S)"
    mv "$filename" "logs/log_$new_filename.log"
fi
source ".venv/bin/activate"
screen -dmS zisterne-py -L -Logfile "logs/latest.log" python -u main.py