#!/usr/bin/env python3
"""Verify deterministic source snapshot against canonical provenance."""
from __future__ import annotations
import argparse, hashlib, json, stat, tempfile, zipfile
from pathlib import Path
from versioning import VERSION


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("snapshot_zip"); ap.add_argument("provenance_json"); a = ap.parse_args()
    snap = Path(a.snapshot_zip).resolve(); provp = Path(a.provenance_json).resolve()
    if not snap.is_file() or not provp.is_file(): raise SystemExit("source snapshot/provenance missing")
    p = json.loads(provp.read_text(encoding="utf-8"))
    if p.get("SourceSchema") != 1: raise SystemExit("unexpected source provenance schema")
    if p.get("AnalysisVersion") != VERSION: raise SystemExit("source provenance version mismatch")
    expected_files = p.get("Files") or {}
    prefix = f"RCInjectAnalysis-{VERSION}/"
    canonical = hashlib.sha256()
    with zipfile.ZipFile(snap) as z:
        names = z.namelist()
        if len(names) != len(set(names)): raise SystemExit("duplicate source snapshot member")
        actual_rels = []
        for name in names:
            pp = Path(name)
            if pp.is_absolute() or ".." in pp.parts or not name.startswith(prefix):
                raise SystemExit(f"unsafe/unexpected source snapshot member: {name}")
            rel = name[len(prefix):]
            if not rel or name.endswith('/'): continue
            actual_rels.append(rel)
        if set(actual_rels) != set(expected_files):
            raise SystemExit(f"source snapshot file-set mismatch: extra={sorted(set(actual_rels)-set(expected_files))} missing={sorted(set(expected_files)-set(actual_rels))}")
        for rel in sorted(expected_files):
            zi = z.getinfo(prefix + rel); data = z.read(zi)
            got_sha = hashlib.sha256(data).hexdigest(); want = expected_files[rel]
            mode = (zi.external_attr >> 16) & 0o7777
            if got_sha != want.get("SHA256"): raise SystemExit(f"source snapshot SHA mismatch: {rel}")
            if len(data) != want.get("Size"): raise SystemExit(f"source snapshot size mismatch: {rel}")
            if f"{mode:04o}" != want.get("Mode"): raise SystemExit(f"source snapshot mode mismatch: {rel}: {mode:04o} != {want.get('Mode')}")
            canonical.update(rel.encode()); canonical.update(b"\0")
            canonical.update(f"{mode:04o}".encode()); canonical.update(b"\0")
            canonical.update(str(len(data)).encode()); canonical.update(b"\0")
            canonical.update(got_sha.encode()); canonical.update(b"\n")
    if canonical.hexdigest() != p.get("TreeSHA256"):
        raise SystemExit("source tree digest mismatch")
    if len(expected_files) != p.get("FileCount"): raise SystemExit("source file-count mismatch")
    print("SOURCE SNAPSHOT PASS")
    print(f"TreeSHA256={p['TreeSHA256']}")
    print(f"FileCount={p['FileCount']}")

if __name__ == '__main__': main()
