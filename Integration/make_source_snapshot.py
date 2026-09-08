#!/usr/bin/env python3
"""Create deterministic zip of release-critical source + provenance JSON."""
from __future__ import annotations
import argparse, json, stat, zipfile
from pathlib import Path
from source_fingerprint import fingerprint, iter_source_files
from versioning import VERSION
from versioning import ROOT

FIXED_DT = (1980, 1, 1, 0, 0, 0)

def zipinfo(name: str, mode: int) -> zipfile.ZipInfo:
    z = zipfile.ZipInfo(name, FIXED_DT)
    z.compress_type = zipfile.ZIP_DEFLATED
    z.create_system = 3
    z.external_attr = ((stat.S_IFREG | mode) & 0xFFFF) << 16
    return z

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output_zip")
    ap.add_argument("provenance_json")
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args()
    root = Path(a.root).resolve(); out = Path(a.output_zip).resolve(); prov = Path(a.provenance_json).resolve()
    fp = fingerprint(root)
    prov.parent.mkdir(parents=True, exist_ok=True)
    prov.write_text(json.dumps(fp, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    prefix = f"RCInjectAnalysis-{VERSION}/"
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w") as z:
        for p in sorted(set(iter_source_files(root)), key=lambda x: x.relative_to(root).as_posix()):
            rel = p.relative_to(root).as_posix()
            mode = int(fp["Files"][rel]["Mode"], 8)
            z.writestr(zipinfo(prefix + rel, mode), p.read_bytes())
    print(f"source snapshot: {out}")
    print(f"source provenance: {prov}")
    print(f"tree sha256: {fp['TreeSHA256']}")

if __name__ == "__main__": main()
