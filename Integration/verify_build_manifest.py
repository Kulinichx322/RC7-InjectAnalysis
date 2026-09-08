#!/usr/bin/env python3
"""Fail closed unless packaged buildinfo matches signed dylib and current release-critical source tree."""
import argparse, hashlib, plistlib, sys
from pathlib import Path
from make_build_manifest import dylib_uuids, build_id
from source_fingerprint import fingerprint
from versioning import VERSION
from versioning import ROOT

BASELINE_SHA256 = "c12b596acd1856677b8fb9753fcebdd88c7601318f10b6b7a8926e2568de687e"
INSTALL_NAME = "@executable_path/Frameworks/RCInjectAnalysis.dylib"
EXPECTED_ARCHS = ["arm64", "arm64e"]

def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("manifest"); ap.add_argument("dylib"); args=ap.parse_args()
    manifest_path=Path(args.manifest); dylib=Path(args.dylib)
    if not manifest_path.is_file() or not dylib.is_file(): raise SystemExit("manifest or dylib missing")
    with manifest_path.open("rb") as f: m=plistlib.load(f)
    expected_uuids=dylib_uuids(dylib); source=fingerprint(ROOT); dylib_sha=sha256(dylib)
    checks={
        "ManifestSchema": m.get("ManifestSchema") == 3,
        "AnalysisVersion": m.get("AnalysisVersion") == VERSION,
        "SourceBaselineExecutableSHA256": m.get("SourceBaselineExecutableSHA256") == BASELINE_SHA256,
        "SourceTreeSHA256": m.get("SourceTreeSHA256") == source["TreeSHA256"],
        "SourceFileCount": m.get("SourceFileCount") == source["FileCount"],
        "DylibSHA256": m.get("DylibSHA256") == dylib_sha,
        "DylibUUIDs": m.get("DylibUUIDs") == expected_uuids,
        "BuildID": m.get("BuildID") == build_id(source["TreeSHA256"], dylib_sha),
        "ExpectedInstallName": m.get("ExpectedInstallName") == INSTALL_NAME,
        "LoadMode": m.get("LoadMode") == "weak",
        "Architectures": m.get("Architectures") == EXPECTED_ARCHS,
        "PackageSuffix": m.get("PackageSuffix") == f"+analysis{VERSION}",
    }
    ok=True
    for key,passed in checks.items(): print(f"{key}: {'PASS' if passed else 'FAIL'}"); ok &= passed
    if not ok: sys.exit(2)
    print(f"build manifest verified; BuildID={m['BuildID']}")
    print(f"SourceTreeSHA256={source['TreeSHA256']}")
    print(f"DylibUUIDs={expected_uuids}")

if __name__ == "__main__": main()
