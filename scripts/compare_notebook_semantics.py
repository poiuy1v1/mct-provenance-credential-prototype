#!/usr/bin/env python3
import json,sys
from pathlib import Path

def semantic_cells(path):
    notebook=json.loads(Path(path).read_text(encoding='utf-8'))
    return [
        {
            'cell_type': cell.get('cell_type'),
            'source': cell.get('source', []),
        }
        for cell in notebook.get('cells', [])
    ]
if semantic_cells(sys.argv[1])!=semantic_cells(sys.argv[2]):
    raise SystemExit('Notebook source/cell-order regression detected')
print('[OK] notebook source and cell order match')
