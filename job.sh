#!/bin/bash

. /home/pi/steezemobile/venv/bin/activate

until (python3 /home/pi/steezemobile/main.py);
do
sleep 10 # wait 10 seconds
done;