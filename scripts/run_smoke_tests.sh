#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
find . -type d -name '__pycache__' -prune -exec rm -rf {} +
find . -type f -name '*.pyc' -delete
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
for f in diagnostic_event_scores.csv diagnostic_sensitivity.csv summary.json verification_results.csv release_validation.json simulation_dry_run_stdout.json simulation_stdout.json verification_workflow_demo_executed.ipynb; do
  cp "outputs/$f" "$TMP/$f"
done
python3 -m json.tool contribution_schema.json >/dev/null
python3 -m json.tool data/example_contributions.json >/dev/null
python3 -m json.tool .zenodo.json >/dev/null
python3 scripts/validate_release.py --json > outputs/release_validation.json
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s MOF_WorkedExample/tests -v
python3 mct_reward_simulation.py --help > outputs/help.txt
python3 mct_reward_simulation.py --dry-run > outputs/simulation_dry_run_stdout.json
python3 mct_reward_simulation.py --input data/example_contributions.json --output-dir outputs > outputs/simulation_stdout.json
jupyter nbconvert --to notebook --execute verification_workflow_demo.ipynb --output verification_workflow_demo_executed.ipynb --output-dir outputs --ExecutePreprocessor.timeout=120 >/dev/null
for f in diagnostic_event_scores.csv diagnostic_sensitivity.csv summary.json verification_results.csv release_validation.json simulation_dry_run_stdout.json simulation_stdout.json; do
  cmp "$TMP/$f" "outputs/$f" || { echo "Regression snapshot mismatch: $f" >&2; exit 1; }
done
python3 scripts/compare_notebook_semantics.py "$TMP/verification_workflow_demo_executed.ipynb" outputs/verification_workflow_demo_executed.ipynb
if find . -type d -name '__pycache__' -o -type f -name '*.pyc' | grep -q .; then echo 'Generated Python bytecode detected' >&2; exit 1; fi
if grep -R -n --exclude-dir=.git --exclude=run_smoke_tests.sh -E 'has_valid_orcid|has_doi|validation_level|verification\.status|evidence_confirmed|scientific_status"|curator_verified_event|Paper 1 v207' .; then echo 'Stale vocabulary detected' >&2; exit 1; fi
echo '[OK] v0.3.3-alpha end-to-end regression snapshots passed'
