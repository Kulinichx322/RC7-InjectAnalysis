#!/usr/bin/env python3
"""Select the unique valid Theos RCInjectAnalysis.dylib; fail closed on ambiguous stale builds."""
import argparse
import hashlib
import struct
from pathlib import Path
from patch_load_command import slices, arch_name, MH_MAGIC_64_LE
from verify_dylib import inspect, MH_DYLIB, EXPECTED


def valid(path: Path) -> bool:
    try:
        buf = path.read_bytes()
        names = []
        for sl in slices(buf):
            name = arch_name(sl.cputype, sl.cpusubtype)
            names.append(name)
            ft, ident = inspect(buf, sl)
            if ft != MH_DYLIB or ident != EXPECTED:
                return False
        return "arm64" in names and "arm64e" in names
    except Exception:
        return False


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("search_root", nargs="?", default=".theos")
    a = ap.parse_args()
    root = Path(a.search_root).resolve()
    if not root.exists():
        raise SystemExit(f"Theos output tree missing: {root}")
    candidates = [p for p in root.rglob("RCInjectAnalysis.dylib") if p.is_file() and valid(p)]
    if not candidates:
        raise SystemExit("no valid universal arm64+arm64e RCInjectAnalysis.dylib found")
    groups = {}
    for p in candidates:
        groups.setdefault(sha(p), []).append(p)
    if len(groups) != 1:
        details = "\n".join(f"  {h[:12]}  {p}" for h, paths in groups.items() for p in paths)
        raise SystemExit("multiple different valid dylib builds found; set RC_ANALYSIS_DYLIB explicitly:\n" + details)
    paths = next(iter(groups.values()))
    # Prefer obj output over packaging staging; then newest path.
    paths.sort(key=lambda p: ("/obj/" in p.as_posix(), p.stat().st_mtime), reverse=True)
    print(paths[0])


if __name__ == "__main__":
    main()
