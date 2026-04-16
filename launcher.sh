#!/usr/bin/env bash
set -e

if [ ! -d ".venv" ]; then
  bash dependance.sh
fi

source .venv/bin/activate
python GUI/main.py
