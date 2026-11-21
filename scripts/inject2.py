import struct, os

NDS='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MD='D:/tsyyds/shijiamoniqi2.11/Sonic 3D Blast (USA, Europe, Korea) (En).md'
OUTDIR='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms'
GP=0x20b6000
DATA_START=GP+0x51000
PAGE=0x10000
NPAGE=64

def swab(b):
    return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

rom=open(MD,'rb').read().ljust(NPAGE*PAGE,b'\xff')
pakdata=swab(rom)
base=bytearray(open(NDS,'rb').read())

DESCS=[(0x410,0xc),(0x454,0x10),(0x49c,0x10),(0x4e4,0x10),(0x52c,0x10),(0x574,0x10)]

def build(name, set_desc_size, mirror=True, data_start=DATA_START):
    nds=bytearray(base)
    for i in range(NPAGE):
        off=data_start+i*PAGE
        nds[off:off+PAGE]=pakdata[i*PAGE:(i+1)*PAGE]
    for tbl_off in (0x8,0x5c0):
        for i in range(128):
            idx=(i & 63) if mirror else i
            addr=data_start+idx*PAGE
            struct.pack_into('<II',nds,GP+tbl_off+8*i,addr,PAGE)
    if set_desc_size is not None:
        for dbase,soff in DESCS:
            struct.pack_into('<I',nds,GP+dbase+soff,set_desc_size)
    label=b'SONIC 3D BLAST'.ljust(0x18,b'\0')
    for no in (0x900,0x918,0x930,0x944):
        nds[GP+no:GP+no+0x18]=label
    p=os.path.join(OUTDIR,name)
    open(p,'wb').write(nds)
    print('WROTE',p,os.path.getsize(p))

# 变体 A: 保守 - 不动 descriptor size
build('Sonic3D_vA_keepdesc.nds', None)
# 变体 B: descriptor size -> 4MB (原 inject.py)
build('Sonic3D_vB_size4m.nds', 0x400000)
