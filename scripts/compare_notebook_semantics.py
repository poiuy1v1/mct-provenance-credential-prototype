#!/usr/bin/env python3
import json, sys
from pathlib import Path

def normalized(path):
    nb=json.loads(Path(path).read_text(encoding='utf-8'))
    for cell in nb.get('cells',[]):
        cell['execution_count']=None
        cell['outputs']=[]
        meta=cell.get('metadata',{})
        for key in list(meta):
            if key in {'execution','collapsed','scrolled'}: meta.pop(key,None)
    nb.get('metadata',{}).pop('widgets',None)
    return nb
if normalized(sys.argv[1])!=normalized(sys.argv[2]):
    raise SystemExit('Notebook semantic regression detected')
print('[OK] notebook semantic snapshot matches')
