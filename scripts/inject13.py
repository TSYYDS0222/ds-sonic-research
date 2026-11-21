import struct, os, time
from lz77_fast import encode as encode2, decode

NDS='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MD='D:/tsyyds/shijiamoniqi2.11/Sonic 3D Blast (USA, Europe, Korea) (En).md'
OUT='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms'
GP=0x20b6000
PAGE=0x10000

def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

rom=open(MD,'rb').read().ljust(64*PAGE,b'\xff')
pakdata=swab(rom)
base=bytearray(open(NDS,'rb').read())

# Build compressed blocks for all 64 pages
print('compressing 64 pages...')
t0=time.time()
comp=[]
for i in range(64):
    page=pakdata[i*PAGE:(i+1)*PAGE]
    c=encode2(page)
    assert decode(c,PAGE)==page, f'page {i} roundtrip fail'
    comp.append(c)
    if i%16==0: print(f'  page {i}: {len(page)} -> {len(c)}')
print(f'compression done in {time.time()-t0:.1f}s, total {sum(len(c) for c in comp)} bytes')

# Write compressed blocks sequentially into the ORIGINAL data pool region.
# Place them right after Game.pak header tables, in an area we allocate inside pak.
# Use the free tail of Game.pak: original compressed pool ends ~0x25d1610.
# We'll write our blocks starting at 0x25d0000? too tight. Use ROM tail but that's out of window.
# KEY INSIGHT: original page table entries already point to valid in-window compressed blocks.
# Replace each block IN PLACE: for entry i, write compressed page (i&63) at that entry's addr,
# and update its size. Keep addr values (in-window) -> no structural change to addresses.
POOL_BASE=0x2380000  # we verified original blocks live around here; use a safe contiguous zone

def build(name, use_existing_addrs=True):
    nds=bytearray(base)
    for tbl in (0x8,0x5c0):
        # First pass: collect original addrs for 128 entries
        orig=[struct.unpack_from('<II',nds,GP+tbl+8*i) for i in range(128)]
        # pack compressed blocks into a contiguous zone starting at first addr
        for i in range(128):
            idx=i&63
            a,s=orig[i]
            c=comp[idx]
            if use_existing_addrs:
                # write at original addr, may overflow into next -> risky if c longer
                nds[a:a+len(c)]=c
                struct.pack_into('<II',nds,GP+tbl+8*i,a,len(c))
    p=os.path.join(OUT,name)
    open(p,'wb').write(nds)
    print('WROTE',name)

# Instead of in-place (overflow risk), do a clean contiguous repack in a dedicated zone.
def build_repack(name, zone):
    nds=bytearray(base)
    cur=zone
    blocks=[]
    for c in comp:
        blocks.append((cur,len(c)))
        nds[cur:cur+len(c)]=c
        cur+=len(c)
    print(f'  repack zone {zone:x}..{cur:x} ({cur-zone} bytes)')
    for tbl in (0x8,0x5c0):
        for i in range(128):
            a,s=blocks[i&63]
            struct.pack_into('<II',nds,GP+tbl+8*i,a,s)
    p=os.path.join(OUT,name)
    open(p,'wb').write(nds)
    print('WROTE',name)

# zone must be in 16MB window AND not overlap CCMS blobs (0x20f7000-0x2377000).
# Original compressed pool 0x2380000..0x25d1610 = 5.2MB, our total ~? 
tot=sum(len(c) for c in comp)
print('total compressed',hex(tot))
# 0x2380000 + tot must stay < 0x25d1610 (end of Game.pak)
print('0x2380000+total =',hex(0x2380000+tot),'pak end 0x25d1610 ->',0x2380000+tot<0x25d1610)
build_repack('Sonic3D_v13_lz.nds', 0x2380000)
