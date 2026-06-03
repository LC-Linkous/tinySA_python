#! /usr/bin/python3
# Quick check that the refactored tsapython package exposes the same public
# API as a reference core.py. Run from the package root (where ./src lives):
#   python verify_api_parity.py path/to/old_core.py
import sys, types, ast

sys.path.insert(0, 'src')
from tsapython import tinySA as New
new_api = sorted(n for n in dir(New) if not n.startswith('__') and callable(getattr(New, n)))

if len(sys.argv) > 1:
    src = open(sys.argv[1], 'rb').read().replace(b'\r\n', b'\n').decode()
    m = types.ModuleType('old'); exec(compile(src, sys.argv[1], 'exec'), m.__dict__)
    Old = m.tinySA
    old_api = sorted(n for n in dir(Old) if not n.startswith('__') and callable(getattr(Old, n)))
    print("identical:", old_api == new_api)
    print("only old:", sorted(set(old_api) - set(new_api)))
    print("only new:", sorted(set(new_api) - set(old_api)))
else:
    print(f"{len(new_api)} public methods exposed by tinySA")
    New()  # smoke-test instantiation
    print("instantiation OK")