#!/usr/bin/env bash
set -euo pipefail

python3 --version
python3 mct_reward_simulation.py --help > outputs/help.txt
python3 mct_reward_simulation.py --dry-run > outputs/simulation_dry_run_stdout.json
python3 mct_reward_simulation.py --input data/example_contributions.json --output-dir outputs > outputs/simulation_stdout.json
python3 -m json.tool contribution_schema.json >/dev/null
python3 -m json.tool data/example_contributions.json >/dev/null
python3 -m json.tool .zenodo.json >/dev/null
python3 - <<'PY'
from pathlib import Path
required = [
    'outputs/mct_scores.csv',
    'outputs/summary.json',
    'outputs/reward_sensitivity.csv',
    'outputs/simulation_stdout.json',
    'outputs/simulation_dry_run_stdout.json',
]
missing = [p for p in required if not Path(p).exists()]
if missing:
    raise SystemExit(f'Missing expected outputs: {missing}')
print('[OK] smoke tests passed')
PY
