import struct, os, zlib

NDS='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MD='D:/tsyyds/shijiamoniqi2.11/Sonic 3D Blast (USA, Europe, Korea) (En).md'
OUT='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms'
GP=0x20b6000
PAGE=0x10000
NPAGE=64

def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

rom=open(MD,'rb').read().ljust(NPAGE*PAGE,b'\xff')
pakdata=swab(rom)
base=bytearray(open(NDS,'rb').read())

# free tail region: 0x3420000 .. 0x3820000 (4MB), 64K-aligned, all 0xFF originally
DATA=0x3420000
# Also make a second copy so CCMS blob base and page tables can both point somewhere valid
BLOBBASE=0x3820000   # another 4MB free region for CCMS-format blob

def build(name, mode):
    nds=bytearray(base)
    # raw swab pages at DATA
    nds[DATA:DATA+NPAGE*PAGE]=pakdata
    hdr=struct.pack('<I4sII', zlib.crc32(pakdata)&0xffffffff, b'CCMS', 0x02027b11, 0x500)
    # CCMS blob: header + same data at BLOBBASE
    nds[BLOBBASE:BLOBBASE+0x10]=hdr
    nds[BLOBBASE+0x10:BLOBBASE+0x10+NPAGE*PAGE]=pakdata

    if mode in ('tables','all'):
        for tbl in (0x8,0x5c0):
            for i in range(128):
                idx=i&63
                struct.pack_into('<II',nds,GP+tbl+8*i, DATA+idx*PAGE, PAGE)

    if mode in ('desc','all'):
        # 6 descriptors step 0x48: base@+0x2c -> BLOBBASE, size@+0xc -> 4MB
        for g in range(6):
            db=GP+0x410+g*0x48
            struct.pack_into('<I',nds,db+0xc,0x400000)      # size
            struct.pack_into('<I',nds,db+0x2c,BLOBBASE)     # CCMS base
            # zero secondary segment refs
            struct.pack_into('<I',nds,db+0x34,0)

    label=b'SONIC 3D BLAST'.ljust(0x18,b'\0')
    for no in (0x900,0x918,0x930,0x944):
        nds[GP+no:GP+no+0x18]=label

    p=os.path.join(OUT,name)
    open(p,'wb').write(nds)
    print('WROTE',name,os.path.getsize(p))

# v7: tables + desc both repointed (DATA raw pages, BLOBBASE CCMS)
build('Sonic3D_v7_all.nds','all')
# v8: only descriptor CCMS base repointed (tables untouched) -> pure CCMS path
build('Sonic3D_v8_ccmsonly.nds','desc')
