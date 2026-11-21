import struct, os

NDS='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MD='D:/Users/江口小学/mortal-kombat.md'
OUT='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms'
GP=0x20b6000
PAGE=0x10000
NP=32

def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)
rom=open(MD,'rb').read().ljust(NP*PAGE,b'\xff')
pakdata=swab(rom)
base=bytearray(open(NDS,'rb').read())

def build(name, data, desc_all=False, desc_slot2=False):
    nds=bytearray(base)
    nds[data:data+NP*PAGE]=pakdata
    for i in range(128):
        struct.pack_into('<II',nds,GP+8+8*i, data+(i%NP)*PAGE, PAGE)
    # descriptor: size@+0xc = 0x200000, pagecount@+0x10 = 0x20
    slots=range(6) if desc_all else ([2] if desc_slot2 else [])
    for g in slots:
        db=GP+0x410+g*0x48
        struct.pack_into('<I',nds,db+0xc,0x200000)   # size
        struct.pack_into('<I',nds,db+0x10,0x20)      # page count
    p=os.path.join(OUT,name)
    open(p,'wb').write(nds)
    print('WROTE',name,'data',hex(data),'desc',('all' if desc_all else ('slot2' if desc_slot2 else 'none')))

# v9: tail data + all descriptors match 2MB/32pages
build('MK_v9_descall.nds', 0x3420000, desc_all=True)
# v10: pool data + all descriptors
build('MK_v10_pool_descall.nds', 0x2380000, desc_all=True)
