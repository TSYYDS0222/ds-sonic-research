import struct, os

NDS='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MD='D:/tsyyds/shijiamoniqi2.11/Sonic 3D Blast (USA, Europe, Korea) (En).md'
OUT='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms'
GP=0x20b6000
PAGE=0x10000
DATA=0x3420000

def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)
rom=open(MD,'rb').read().ljust(64*PAGE,b'\xff')
pakdata=swab(rom)
base=bytearray(open(NDS,'rb').read())

def build(name, desc_size=None, rename=False):
    nds=bytearray(base)
    nds[DATA:DATA+64*PAGE]=pakdata
    # only the clean @0x8 page table
    for i in range(128):
        idx=i&63
        struct.pack_into('<II',nds,GP+8+8*i, DATA+idx*PAGE, PAGE)
    # descriptor size only (step 0x48, size@+0xc), leave base/name/flags alone
    if desc_size is not None:
        for g in range(6):
            struct.pack_into('<I',nds,GP+0x410+g*0x48+0xc, desc_size)
    if rename:
        label=b'SONIC 3D BLAST'.ljust(0x18,b'\0')
        for no in (0x900,0x918,0x930,0x944):
            nds[GP+no:GP+no+0x18]=label
    p=os.path.join(OUT,name)
    open(p,'wb').write(nds)
    print('WROTE',name,'desc_size',hex(desc_size) if desc_size else None,'rename',rename)

# v16a: + desc size 4MB (all 6 slots)
build('Sonic3D_v16a_descsize.nds', 0x400000, False)
# v16b: + desc size + rename
build('Sonic3D_v16b_descsize_rename.nds', 0x400000, True)
