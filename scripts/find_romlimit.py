import struct, re

d=open('rom.bin','rb').read()
a9=d[0x4000:0x4000+537728]
base=0x2004000

# Search for 3MB limit constant 0x306800 and variants
for c in (0x306800,0x300000,0x306000,0x400000,0x23FF000,0x023FF000):
    pat=struct.pack('<I',c)
    hits=[base+m.start() for m in re.finditer(re.escape(pat),a9)]
    print(f'{c:08x}: {len(hits)} hits {[hex(h) for h in hits[:10]]}')

# jEnesisDSPlus patches address 0x02002058 in the standalone jEnesisDS.
# In SCC the code is relocated (ARM9 base 0x2004000). Look for the analogous
# global holding ROM size: search the constant 0x306800 as halfword pairs too.
print('\n=== halfword 0x6800 / 0x3068 ===')
for h in (0x6800,0x3068,0x5830):
    pat=struct.pack('<H',h)
    hits=[base+m.start() for m in re.finditer(re.escape(pat),a9)]
    print(f'{h:04x}: {len(hits)} {[hex(x) for x in hits[:10]]}')

# Search code comparing against 0x306800 (cmp rX, #imm unlikely; literal load)
print('\n=== cmp with rom size patterns ===')
for m in re.finditer(rb'cmp\s',a9[:0]):
    pass
