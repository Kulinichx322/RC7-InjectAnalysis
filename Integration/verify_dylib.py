#!/usr/bin/env python3
"""Check the Analysis dylib has arm64 + arm64e slices and the expected LC_ID_DYLIB."""
import argparse, struct, sys
from pathlib import Path
from patch_load_command import slices, arch_name, MH_MAGIC_64_LE
LC_ID_DYLIB=0x0D
MH_DYLIB=0x6
EXPECTED='@executable_path/Frameworks/RCInjectAnalysis.dylib'

def inspect(buf, sl):
    b=sl.offset
    if struct.unpack_from('<I',buf,b)[0] != MH_MAGIC_64_LE: raise ValueError('not 64-bit Mach-O')
    filetype=struct.unpack_from('<I',buf,b+12)[0]
    ncmds,sizeofcmds=struct.unpack_from('<II',buf,b+16)
    pos=b+32; end=pos+sizeofcmds; ident=None
    for _ in range(ncmds):
        cmd,cs=struct.unpack_from('<II',buf,pos)
        if cs<8 or pos+cs>end: raise ValueError('invalid load command')
        if cmd==LC_ID_DYLIB and cs>=24:
            no=struct.unpack_from('<I',buf,pos+8)[0]
            if 0<no<cs:
                ident=bytes(buf[pos+no:pos+cs]).split(b'\0',1)[0].decode('utf-8','replace')
        pos+=cs
    return filetype,ident

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('dylib'); ap.add_argument('--id',default=EXPECTED); a=ap.parse_args()
    buf=Path(a.dylib).read_bytes(); found=[]; ok=True
    for sl in slices(buf):
        name=arch_name(sl.cputype,sl.cpusubtype); found.append(name)
        ft,ident=inspect(buf,sl)
        good=(ft==MH_DYLIB and ident==a.id)
        print(f'{name}: filetype=0x{ft:x} id={ident!r} ok={good}')
        ok &= good
    for req in ('arm64','arm64e'):
        if req not in found:
            print(f'missing required slice: {req}',file=sys.stderr); ok=False
    if not ok: sys.exit(2)
if __name__=='__main__': main()
