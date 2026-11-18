#!/usr/bin/env bash
# Starts the clock. Run this right after you start your screen recording.
cd "$(dirname "$0")" || exit 1
mkdir -p submission

if [ -f submission/started_at.txt ]; then
  echo "The clock already started at $(cat submission/started_at.txt)."
  exit 0
fi

date -u +"%Y-%m-%dT%H:%M:%SZ" > submission/started_at.txt
echo "The clock started at $(cat submission/started_at.txt) (UTC)."
echo "You have 90 minutes. Open CANDIDATE.md and begin with Part 1."
