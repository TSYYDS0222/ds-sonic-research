import struct, os

NDS='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MD='D:/Users/江口小学/mortal-kombat.md'
OUT='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms'
GP=0x20b6000
PAGE=0x10000
DATA=0x3420000

def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

rom=open(MD,'rb').read()
npages=(len(rom)+PAGE-1)//PAGE
rom=rom.ljust(npages*PAGE,b'\xff')
pakdata=swab(rom)
base=bytearray(open(NDS,'rb').read())
print('ROM pages',npages)

def build(name, rename=False, descsize=None):
    nds=bytearray(base)
    nds[DATA:DATA+npages*PAGE]=pakdata
    # only clean @0x8 page table; entries map to page (i % npages)
    for i in range(128):
        idx=i%npages
        struct.pack_into('<II',nds,GP+8+8*i, DATA+idx*PAGE, PAGE)
    if descsize is not None:
        for g in range(6):
            struct.pack_into('<I',nds,GP+0x410+g*0x48+0xc,descsize)
    if rename:
        label=b'MORTAL KOMBAT'.ljust(0x18,b'\0')
        for no in (0x900,0x918,0x930,0x944):
            nds[GP+no:GP+no+0x18]=label
    p=os.path.join(OUT,name)
    open(p,'wb').write(nds)
    print('WROTE',name)

# Main: verified-good v15a recipe (only @0x8 table, nothing else)
build('MK_v1_clean.nds')
# Alt: with game names changed
build('MK_v2_rename.nds', rename=True)
