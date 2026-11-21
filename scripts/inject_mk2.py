import struct, os

NDS='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MD='D:/Users/江口小学/mortal-kombat.md'
OUT='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms'
GP=0x20b6000
PAGE=0x10000
DATA=0x3420000
NP=32

def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)
rom=open(MD,'rb').read().ljust(NP*PAGE,b'\xff')
pakdata=swab(rom)
base=bytearray(open(NDS,'rb').read())

def build(name, mode):
    nds=bytearray(base)
    nds[DATA:DATA+NP*PAGE]=pakdata
    # get original @0x8 table
    orig=[struct.unpack_from('<II',base,GP+8+8*i) for i in range(128)]
    for i in range(128):
        if mode=='low32':
            if i<NP:
                struct.pack_into('<II',nds,GP+8+8*i, DATA+i*PAGE, PAGE)
            # else keep original stub entries untouched
        elif mode=='mirror32':
            struct.pack_into('<II',nds,GP+8+8*i, DATA+(i%NP)*PAGE, PAGE)
        elif mode=='mirror64':
            struct.pack_into('<II',nds,GP+8+8*i, DATA+(i%64)*PAGE, PAGE)
    p=os.path.join(OUT,name)
    open(p,'wb').write(nds)
    print('WROTE',name)

build('MK_v3_low32only.nds','low32')
build('MK_v4_mirror32.nds','mirror32')   # same as v1 (control)
build('MK_v5_mirror64.nds','mirror64')
