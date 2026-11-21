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

# Find a truly FREE in-window region: scan FAT gaps between 0x2000000 and 0x3000000
# file7 (Game.pak) ends 0x25d1610, file8 starts 0x25df000 -> small gap
# But Game.pak itself has a large internal free area at its tail (after 0x25d1610 is another file)
# Best: use 0x25df0000 area? no. Use the CCMS-less zone we know pages live: original pages are in data pool
# Actually simplest & safest: overwrite the ORIGINAL compressed page pool in-place (0x2380000+)
# but store as RAW pages with size=0x10000, and only touch page-table entries.
# CCMS blobs (0x20f7000-0x2377000) stay intact.

def build(name, data_addr, mirror):
    nds=bytearray(base)
    nds[data_addr:data_addr+64*PAGE]=pakdata
    for tbl in (0x8,0x5c0):
        for i in range(128):
            idx=(i&63) if mirror else i
            struct.pack_into('<II',nds,GP+tbl+8*i, data_addr+idx*PAGE, PAGE)
    p=os.path.join(OUT,name)
    open(p,'wb').write(nds)
    print('WROTE',name,'data@',hex(data_addr))

# v12: data at 0x25df000 is file8 start (screens dat) - avoid.
# Use Game.pak internal tail beyond original data: original pak ends 0x25d1610, data pool to there.
# 0x2380000 + 0x400000 = 0x2780000 < 0x25d1610? NO: 0x2780000 > 0x25d1610. Overlaps file8!
# Recompute: Game.pak = 0x20b6000..0x25d1610. Max safe 64-page block inside pak:
# need 0x400000 bytes ending <= 0x25d1610 -> start <= 0x21d1610. But that overlaps CCMS blobs.
# So in-window free 4MB contiguous inside a single file does NOT exist unless we overwrite blobs.
# => Use ROM tail (out of window) OR overwrite the whole Game.pak data (blobs included).
# Since v6 showed blob corruption = boot black, use tail but verify emulator window claim is wrong.
build('Sonic3D_v12_tail64k.nds', 0x3420000, True)
