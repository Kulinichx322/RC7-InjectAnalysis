#!/usr/bin/env python3
"""Create the read-only package identity manifest after the Analysis dylib is signed."""
import argparse
import hashlib
import plistlib
import struct
from pathlib import Path
from patch_load_command import slices, arch_name, MH_MAGIC_64_LE
from source_fingerprint import fingerprint
from versioning import VERSION
from versioning import ROOT

BASELINE_SHA256 = "c12b596acd1856677b8fb9753fcebdd88c7601318f10b6b7a8926e2568de687e"
INSTALL_NAME = "@executable_path/Frameworks/RCInjectAnalysis.dylib"
LC_UUID = 0x1B


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fmt_uuid(b: bytes) -> str:
    h = b.hex().upper()
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def dylib_uuids(path: Path) -> dict[str, str]:
    buf = path.read_bytes(); out = {}
    for sl in slices(buf):
        name = arch_name(sl.cputype, sl.cpusubtype); base = sl.offset
        if struct.unpack_from('<I', buf, base)[0] != MH_MAGIC_64_LE:
            raise SystemExit(f"{name}: not a 64-bit Mach-O slice")
        ncmds, sizeofcmds = struct.unpack_from('<II', buf, base + 16)
        pos = base + 32; end = pos + sizeofcmds; found = None
        for _ in range(ncmds):
            cmd, cmdsize = struct.unpack_from('<II', buf, pos)
            if cmdsize < 8 or pos + cmdsize > end: raise SystemExit(f"{name}: invalid load-command table")
            if cmd == LC_UUID and cmdsize >= 24:
                found = fmt_uuid(bytes(buf[pos + 8:pos + 24])); break
            pos += cmdsize
        if not found: raise SystemExit(f"{name}: LC_UUID missing")
        out[name] = found
    for req in ("arm64", "arm64e"):
        if req not in out: raise SystemExit(f"missing required UUID slice: {req}")
    return out


def build_id(source_sha: str, dylib_sha: str) -> str:
    material = "\0".join(("RCInjectAnalysis", VERSION, source_sha, dylib_sha, BASELINE_SHA256)).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("dylib"); ap.add_argument("output_plist"); args = ap.parse_args()
    dylib = Path(args.dylib); out = Path(args.output_plist)
    if not dylib.is_file(): raise SystemExit(f"missing dylib: {dylib}")
    source = fingerprint(ROOT); dylib_sha = sha256(dylib)
    manifest = {
        "ManifestSchema": 3,
        "AnalysisVersion": VERSION,
        "SourceBaselineExecutableSHA256": BASELINE_SHA256,
        "SourceTreeSHA256": source["TreeSHA256"],
        "SourceFileCount": source["FileCount"],
        "DylibSHA256": dylib_sha,
        "DylibUUIDs": dylib_uuids(dylib),
        "BuildID": build_id(source["TreeSHA256"], dylib_sha),
        "ExpectedInstallName": INSTALL_NAME,
        "LoadMode": "weak",
        "Architectures": ["arm64", "arm64e"],
        "PackageSuffix": f"+analysis{VERSION}",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("wb") as f: plistlib.dump(manifest, f, fmt=plistlib.FMT_XML, sort_keys=True)
    print(f"build manifest created: {out}")
    print(f"BuildID={manifest['BuildID']}")
    print(f"SourceTreeSHA256={manifest['SourceTreeSHA256']}")
    print(f"DylibSHA256={manifest['DylibSHA256']}")
    print(f"DylibUUIDs={manifest['DylibUUIDs']}")

if __name__ == "__main__": main()
