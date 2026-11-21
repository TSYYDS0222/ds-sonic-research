import struct, os

NDS='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MD='D:/tsyyds/shijiamoniqi2.11/Sonic 3D Blast (USA, Europe, Korea) (En).md'
OUT='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms'
GP=0x20b6000
PAGE=0x10000

def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

rom=open(MD,'rb').read().ljust(64*PAGE,b'\xff')
pakdata=swab(rom)
base=bytearray(open(NDS,'rb').read())
DATA=0x3420000

def build(name, tbls, mirror=True):
    nds=bytearray(base)
    nds[DATA:DATA+64*PAGE]=pakdata
    for tbl in tbls:
        for i in range(128):
            idx=(i&63) if mirror else i
            struct.pack_into('<II',nds,GP+tbl+8*i, DATA+idx*PAGE, PAGE)
    p=os.path.join(OUT,name)
    open(p,'wb').write(nds)
    print('WROTE',name,'tables',[hex(t) for t in tbls])

# v14a: only table @0x8 ; v14b: only @0x5c0 ; v14c: both
build('Sonic3D_v14a_t8.nds',(0x8,))
build('Sonic3D_v14b_t5c0.nds',(0x5c0,))
build('Sonic3D_v14c_both.nds',(0x8,0x5c0))
