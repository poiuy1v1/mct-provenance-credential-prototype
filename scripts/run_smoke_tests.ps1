$ErrorActionPreference = 'Stop'
python scripts/run_smoke_tests.py --notebook-backend nbclient
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
