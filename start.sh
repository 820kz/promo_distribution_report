#!/bin/bash
python telegram_reports.py & hypercorn api_service_reports:app --bind 0.0.0.0:10503 --workers 4

