import struct, os

NDS='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MD='D:/tsyyds/shijiamoniqi2.11/Sonic 3D Blast (USA, Europe, Korea) (En).md'
OUT='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms'
GP=0x20b6000
PAGE=0x10000
NPAGE=64
NEW=0x3420000   # file offset in 12MB free tail; address value == file offset

def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

rom=open(MD,'rb').read().ljust(NPAGE*PAGE,b'\xff')
pakdata=swab(rom)
base=bytearray(open(NDS,'rb').read())

def build(name, set_desc_size=False):
    nds=bytearray(base)
    # 1. write swabbed ROM into free tail (no original data touched)
    nds[NEW:NEW+NPAGE*PAGE]=pakdata
    # 2. redirect BOTH page tables to new pages
    for tbl in (0x8,0x5c0):
        for i in range(128):
            idx=i&63
            addr=NEW+idx*PAGE
            struct.pack_into('<II',nds,GP+tbl+8*i,addr,PAGE)
    # 3. rename 4 game labels
    label=b'SONIC 3D BLAST'.ljust(0x18,b'\0')
    for no in (0x900,0x918,0x930,0x944):
        nds[GP+no:GP+no+0x18]=label
    # 4. optionally bump descriptor sizes to 4MB (step 0x48, size @+0xc)
    if set_desc_size:
        for g in range(6):
            struct.pack_into('<I',nds,GP+0x410+g*0x48+0xc,0x400000)
    p=os.path.join(OUT,name)
    open(p,'wb').write(nds)
    print('WROTE',name,os.path.getsize(p))

build('Sonic3D_v3_safe.nds',False)
build('Sonic3D_v4_desc4m.nds',True)
