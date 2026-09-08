#!/usr/bin/env python3
"""Single version source for RCInjectAnalysis integration tooling."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "VERSION"


def analysis_version() -> str:
    value = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not value or any(c not in "0123456789." for c in value):
        raise RuntimeError(f"invalid VERSION file: {value!r}")
    return value


VERSION = analysis_version()
PACKAGE_SUFFIX = f"+analysis{VERSION}"
