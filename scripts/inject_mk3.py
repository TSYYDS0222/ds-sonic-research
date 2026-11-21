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

def build(name, data, mode, desc_sram=None):
    nds=bytearray(base)
    nds[data:data+NP*PAGE]=pakdata
    for i in range(128):
        if mode=='mirror32':
            struct.pack_into('<II',nds,GP+8+8*i, data+(i%NP)*PAGE, PAGE)
        elif mode=='low32':
            if i<NP: struct.pack_into('<II',nds,GP+8+8*i, data+i*PAGE, PAGE)
    if desc_sram:
        # copy SRAM config from Sonic3 slot (g2) into slot0
        src=GP+0x410+2*0x48
        dst=GP+0x410+0*0x48
        for off in (0x10,0x14,0x18):
            v=struct.unpack_from('<I',base,src+off)[0]
            struct.pack_into('<I',nds,dst+off,v)
    p=os.path.join(OUT,name)
    open(p,'wb').write(nds)
    print('WROTE',name)

# Data in Game.pak pool (in-window, where original compressed blocks live)
build('MK_v6_pool_mirror.nds', 0x2380000, 'mirror32')
build('MK_v7_pool_low32.nds', 0x2380000, 'low32')
# Tail + SRAM config
build('MK_v8_tail_sram.nds', 0x3420000, 'mirror32', desc_sram=True)
