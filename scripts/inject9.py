import struct, os

NDS='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MD='D:/tsyyds/shijiamoniqi2.11/Sonic 3D Blast (USA, Europe, Korea) (En).md'
OUT='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms'
GP=0x20b6000
PAGE=0x10000
DATA=0x3420000   # free tail

def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

rom=open(MD,'rb').read().ljust(64*PAGE,b'\xff')
pakdata=swab(rom)
base=bytearray(open(NDS,'rb').read())

def build(name, tables):
    nds=bytearray(base)
    nds[DATA:DATA+64*PAGE]=pakdata
    for tbl in tables:
        for i in range(128):
            idx=i&63
            struct.pack_into('<II',nds,GP+tbl+8*i, DATA+idx*PAGE, PAGE)
    label=b'SONIC 3D BLAST'.ljust(0x18,b'\0')
    for no in (0x900,0x918,0x930,0x944):
        nds[GP+no:GP+no+0x18]=label
    p=os.path.join(OUT,name)
    open(p,'wb').write(nds)
    print('WROTE',name)

# v9a: only table 0x8 ; v9b: only table 0x5c0 ; v9c: both (same as v3)
build('Sonic3D_v9a_tbl8.nds',(0x8,))
build('Sonic3D_v9b_tbl5c0.nds',(0x5c0,))
build('Sonic3D_v9c_both.nds',(0x8,0x5c0))
