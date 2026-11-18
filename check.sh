#!/usr/bin/env bash
# Runs a health check on your work and saves the report to check-results.txt.
cd "$(dirname "$0")" || exit 1
python checker/health_check.py
