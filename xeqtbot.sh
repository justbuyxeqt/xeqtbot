#!/bin/bash

cd "$(dirname "$0")"
git pull
pip3 install -r requirements.txt
python3 main.py