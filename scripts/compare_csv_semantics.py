#!/usr/bin/env python3
import csv,sys
from pathlib import Path
def rows(path):
    with Path(path).open(newline='',encoding='utf-8') as handle:
        return list(csv.DictReader(handle))
if rows(sys.argv[1])!=rows(sys.argv[2]):
    raise SystemExit(f'CSV semantic regression detected: {sys.argv[1]} != {sys.argv[2]}')
print(f'[OK] CSV snapshot matches: {Path(sys.argv[2]).name}')
