#!/bin/bash
source /home/property/python/venv/bin/activate
python rentallscraper.py
python salesscraper.py
python rentavgscraper.py
python roi.py
deactivate