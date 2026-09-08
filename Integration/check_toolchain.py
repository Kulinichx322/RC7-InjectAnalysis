#!/usr/bin/env python3
"""Preflight the real Theos/iOS SDK environment before building RCInjectAnalysis."""
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional
from versioning import VERSION

REQUIRED_COMMANDS = ("make", "python3", "dpkg-deb", "ldid")


def cmd_version(cmd: str) -> str:
    attempts = ([cmd, "--version"], [cmd, "-v"])
    for argv in attempts:
        try:
            p = subprocess.run(argv, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=5)
            out = (p.stdout or "").strip().splitlines()
            if out:
                return out[0][:200]
        except Exception:
            pass
    return "available"


def find_sdk(theos: Path) -> Optional[Path]:
    sdkdir = theos / "sdks"
    candidates = sorted(sdkdir.glob("iPhoneOS*.sdk")) if sdkdir.is_dir() else []
    if candidates:
        return candidates[-1]
    xcrun = shutil.which("xcrun")
    if xcrun:
        try:
            value = subprocess.check_output([xcrun, "--sdk", "iphoneos", "--show-sdk-path"], text=True, timeout=10).strip()
            p = Path(value)
            if p.is_dir():
                return p
        except Exception:
            pass
    return None


def main() -> None:
    errors = []
    print(f"RCInjectAnalysis toolchain preflight — {VERSION}")
    print(f"host={platform.system()} {platform.machine()} python={platform.python_version()}")
    if sys.version_info < (3, 9):
        errors.append("Python >= 3.9 is required")

    for cmd in REQUIRED_COMMANDS:
        path = shutil.which(cmd)
        if not path:
            errors.append(f"missing command: {cmd}")
            print(f"{cmd}: MISSING")
        else:
            print(f"{cmd}: {path} ({cmd_version(cmd)})")

    theos_env = os.environ.get("THEOS", "").strip()
    if not theos_env:
        errors.append("THEOS environment variable is not set")
        theos = None
        print("THEOS: MISSING")
    else:
        theos = Path(theos_env).expanduser().resolve()
        print(f"THEOS: {theos}")
        if not (theos / "makefiles/common.mk").is_file():
            errors.append(f"invalid THEOS tree: {theos / 'makefiles/common.mk'} missing")

    sdk = find_sdk(theos) if theos else None
    if not sdk:
        errors.append("iPhoneOS SDK not found under $THEOS/sdks and xcrun iphoneos SDK unavailable")
        print("iPhoneOS SDK: MISSING")
    else:
        print(f"iPhoneOS SDK: {sdk}")
        for fw in ("Foundation", "UIKit"):
            framework = sdk / f"System/Library/Frameworks/{fw}.framework"
            if not framework.exists():
                errors.append(f"SDK missing framework: {fw}")

    print("packaging metadata: host uid/gid independent (baseline-aware tar repacker)")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(2)
    print("TOOLCHAIN PREFLIGHT PASS")


if __name__ == "__main__":
    main()
