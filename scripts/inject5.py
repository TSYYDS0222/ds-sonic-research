import struct, os

NDS='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MD='D:/tsyyds/shijiamoniqi2.11/Sonic 3D Blast (USA, Europe, Korea) (En).md'
OUT='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms'
GP=0x20b6000
PAGE=0x10000
NPAGE=64
DATA=0x3420000          # 64K-aligned swab ROM data
BLOBHDR=DATA-0x10       # CCMS header sits in tail of previous page

def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

rom=open(MD,'rb').read().ljust(NPAGE*PAGE,b'\xff')
pakdata=swab(rom)
base=bytearray(open(NDS,'rb').read())

# CCMS header: crc32(placeholder), "CCMS", ver, gameid
import zlib
hdr=struct.pack('<I4sII', zlib.crc32(pakdata)&0xffffffff, b'CCMS', 0x02027b11, 0)

def build(name):
    nds=bytearray(base)
    # 1. write header + data into free tail (no original bytes touched)
    nds[BLOBHDR:BLOBHDR+0x10]=hdr
    nds[DATA:DATA+NPAGE*PAGE]=pakdata
    # 2. redirect both ROM page tables
    for tbl in (0x8,0x5c0):
        for i in range(128):
            idx=i&63
            struct.pack_into('<II',nds,GP+tbl+8*i,DATA+idx*PAGE,PAGE)
    # 3. fix all 6 descriptors (step 0x48): size@+0xc -> 4MB, base@+0x2c -> blob hdr
    for g in range(6):
        db=0x410+g*0x48
        struct.pack_into('<I',nds,GP+db+0xc,0x400000)     # size
        struct.pack_into('<I',nds,GP+db+0x2c,BLOBHDR)     # CCMS blob base
        # drop any second segment (+0x34) that pointed to old blob
        struct.pack_into('<I',nds,GP+db+0x34,0)
    # 4. rename game labels
    label=b'SONIC 3D BLAST'.ljust(0x18,b'\0')
    for no in (0x900,0x918,0x930,0x944):
        nds[GP+no:GP+no+0x18]=label
    p=os.path.join(OUT,name)
    open(p,'wb').write(nds)
    print('WROTE',name,os.path.getsize(p))

build('Sonic3D_v5_full.nds')
