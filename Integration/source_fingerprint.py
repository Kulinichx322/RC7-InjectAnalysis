#!/usr/bin/env python3
"""Canonical fingerprint of release-critical RCInjectAnalysis source files."""
from __future__ import annotations
import argparse, hashlib, json, os, stat
from pathlib import Path
from versioning import VERSION
from versioning import ROOT

TOP_FILES = ("VERSION", "Makefile")
TOP_DIRS = ("Sources", "Integration")
EXCLUDED_NAMES = {"__pycache__", ".DS_Store"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def iter_source_files(root: Path):
    root = root.resolve()
    for rel in TOP_FILES:
        p = root / rel
        if not p.is_file():
            raise SystemExit(f"missing release-critical source file: {rel}")
        yield p
    for d in TOP_DIRS:
        base = root / d
        if not base.is_dir():
            raise SystemExit(f"missing release-critical source directory: {d}")
        for p in sorted(base.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(root)
            if any(part in EXCLUDED_NAMES for part in rel.parts):
                continue
            if p.suffix in EXCLUDED_SUFFIXES:
                continue
            yield p


def file_mode(p: Path) -> int:
    return stat.S_IMODE(p.stat().st_mode)


def fingerprint(root: Path) -> dict:
    root = root.resolve()
    files = {}
    canonical = hashlib.sha256()
    for p in sorted(set(iter_source_files(root)), key=lambda x: x.relative_to(root).as_posix()):
        rel = p.relative_to(root).as_posix()
        data = p.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        mode = file_mode(p)
        size = len(data)
        files[rel] = {"SHA256": digest, "Mode": f"{mode:04o}", "Size": size}
        canonical.update(rel.encode("utf-8")); canonical.update(b"\0")
        canonical.update(f"{mode:04o}".encode("ascii")); canonical.update(b"\0")
        canonical.update(str(size).encode("ascii")); canonical.update(b"\0")
        canonical.update(digest.encode("ascii")); canonical.update(b"\n")
    return {
        "SourceSchema": 1,
        "AnalysisVersion": VERSION,
        "TreeSHA256": canonical.hexdigest(),
        "FileCount": len(files),
        "Files": files,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=str(ROOT))
    ap.add_argument("--json-out")
    a = ap.parse_args()
    result = fingerprint(Path(a.root))
    if a.json_out:
        out = Path(a.json_out).resolve(); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"source provenance: {out}")
    print(f"SourceTreeSHA256={result['TreeSHA256']}")
    print(f"SourceFileCount={result['FileCount']}")

if __name__ == "__main__":
    main()
