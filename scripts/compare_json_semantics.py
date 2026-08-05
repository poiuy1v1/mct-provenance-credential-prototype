#!/usr/bin/env python3
import json,sys
if json.load(open(sys.argv[1],encoding='utf-8'))!=json.load(open(sys.argv[2],encoding='utf-8')):raise SystemExit('JSON semantic regression detected')
print('[OK] JSON snapshot matches')
