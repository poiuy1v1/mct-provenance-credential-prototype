#!/usr/bin/env bash
set -euo pipefail
python3 scripts/run_smoke_tests.py --notebook-backend nbclient
