#!/usr/bin/env python3
"""Compare two entitlement plists semantically (dictionary equality)."""
import argparse, plistlib, sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('expected'); ap.add_argument('actual'); a=ap.parse_args()
    e=plistlib.loads(Path(a.expected).read_bytes())
    x=plistlib.loads(Path(a.actual).read_bytes())
    if e != x:
        ek=set(e); xk=set(x)
        print('entitlements mismatch', file=sys.stderr)
        print('missing keys:', sorted(ek-xk), file=sys.stderr)
        print('extra keys:', sorted(xk-ek), file=sys.stderr)
        changed=[k for k in sorted(ek & xk) if e[k] != x[k]]
        print('changed keys:', changed, file=sys.stderr)
        sys.exit(2)
    print(f'entitlements identical ({len(e)} keys)')
if __name__=='__main__': main()
