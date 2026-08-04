#!/usr/bin/env python3
import csv,sys
def rows(p):
 with open(p,newline='',encoding='utf-8') as h:return list(csv.DictReader(h))
if rows(sys.argv[1])!=rows(sys.argv[2]):raise SystemExit('CSV semantic regression detected')
print('[OK] CSV snapshot matches')
