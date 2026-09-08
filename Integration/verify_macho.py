#!/usr/bin/env python3
"""Verify every arm64/arm64e slice contains exactly one expected weak Analysis load."""
import argparse, struct, sys
from pathlib import Path
from patch_load_command import slices, arch_name, MH_MAGIC_64_LE, LC_LOAD_WEAK_DYLIB


def dylib_commands(buf: bytes, sl):
    base=sl.offset
    if struct.unpack_from('<I',buf,base)[0] != MH_MAGIC_64_LE: raise ValueError('not MH_MAGIC_64')
    ncmds,sizeofcmds=struct.unpack_from('<II',buf,base+16)
    pos=base+32; end=pos+sizeofcmds; out=[]
    for _ in range(ncmds):
        if pos+8>end: raise ValueError('truncated load command')
        cmd,cs=struct.unpack_from('<II',buf,pos)
        if cs<8 or pos+cs>end: raise ValueError('invalid load command')
        if cs>=24 and cmd in {0x0c,0x80000018,0x8000001f,0x80000023,0x20,0x0d}:
            no=struct.unpack_from('<I',buf,pos+8)[0]
            if 0<no<cs:
                name=bytes(buf[pos+no:pos+cs]).split(b'\0',1)[0].decode('utf-8','replace')
                out.append((cmd,name))
        pos+=cs
    return ncmds,sizeofcmds,out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('macho'); ap.add_argument('--path',default='@executable_path/Frameworks/RCInjectAnalysis.dylib'); a=ap.parse_args()
    b=Path(a.macho).read_bytes(); ok=True; found_arch=[]
    for sl in slices(b):
        name=arch_name(sl.cputype,sl.cpusubtype); found_arch.append(name)
        n,sz,cmds=dylib_commands(b,sl)
        hits=[cmd for cmd,path in cmds if path==a.path]
        good=(hits == [LC_LOAD_WEAK_DYLIB])
        print(f'{name}: ncmds={n} sizeofcmds={sz} analysis_hits={len(hits)} weak={good}')
        if not good: ok=False
    for req in ('arm64','arm64e'):
        if req not in found_arch:
            print(f'missing required slice: {req}',file=sys.stderr); ok=False
    if not ok: sys.exit(2)
if __name__=='__main__': main()
