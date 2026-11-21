import struct, os, zlib

NDS='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MD='D:/tsyyds/shijiamoniqi2.11/Sonic 3D Blast (USA, Europe, Korea) (En).md'
OUT='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms'
GP=0x20b6000
SLOT5=0x2377000     # existing 4MB CCMS blob, gameid=0x500 (likely unused slot)

def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

rom=open(MD,'rb').read().ljust(0x400000,b'\xff')
pakdata=swab(rom)
base=bytearray(open(NDS,'rb').read())

def build(name):
    nds=bytearray(base)
    # overwrite blob slot5 data region, keep CCMS header in place (update crc field)
    nds[SLOT5+0x10:SLOT5+0x10+0x400000]=pakdata
    struct.pack_into('<I',nds,SLOT5, zlib.crc32(pakdata)&0xffffffff)
    # rename the 4 visible game labels only
    label=b'SONIC 3D BLAST'.ljust(0x18,b'\0')
    for no in (0x900,0x918,0x930,0x944):
        nds[GP+no:GP+no+0x18]=label
    p=os.path.join(OUT,name)
    open(p,'wb').write(nds)
    print('WROTE',name,os.path.getsize(p))

build('Sonic3D_v6_slot5.nds')
