#!/usr/bin/env python3
import json,sys
from pathlib import Path
left=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
right=json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))
if left!=right:
    raise SystemExit(f'JSON semantic regression detected: {sys.argv[1]} != {sys.argv[2]}')
print(f'[OK] JSON snapshot matches: {Path(sys.argv[2]).name}')
