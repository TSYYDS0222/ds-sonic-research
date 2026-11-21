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

def build(name, data_addr, tbl=0x8):
    nds=bytearray(base)
    nds[data_addr:data_addr+64*PAGE]=pakdata
    for i in range(128):
        idx=i&63
        struct.pack_into('<II',nds,GP+tbl+8*i, data_addr+idx*PAGE, PAGE)
    p=os.path.join(OUT,name)
    open(p,'wb').write(nds)
    print('WROTE',name,'data',hex(data_addr),'tbl',hex(tbl))

# data at tail, only @0x8 table
build('Sonic3D_v15a_tail_t8.nds', 0x3420000, 0x8)
# data inside Game.pak pool overwrite (0x2380000), only @0x8
build('Sonic3D_v15b_pool_t8.nds', 0x2380000, 0x8)
