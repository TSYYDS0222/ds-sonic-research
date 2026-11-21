import struct, zlib, re

ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d=open(ROM,'rb').read()

BLOBS=[0x20f7000,0x2197000,0x2267000,0x2347000,0x2357000,0x2367000,0x2377000]
SIZES=[0x80000,0x100000,0x200000,0x300000,None,0x400000,0x400000]

def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

for base,sz in zip(BLOBS,SIZES):
    blob=d[base:base+16]
    crc,magic,ver,gid=struct.unpack('<I4sII',blob)
    print(f'blob@{base:08x} crc={crc:08x} magic={magic} ver={ver:08x} gameid={gid:08x}')
    # dump header 0x40
    print('  hdr:',d[base:base+0x40].hex())
    # swab data after +0x10, look for ROM header at various offsets
    data=d[base+0x10:base+0x10+(sz or 0x1000)]
    s=swab(data)
    print('  swab[0:0x30]:',s[:0x30])
    # search SEGA in first 0x400
    for kw in (b'SEGA',b'GENESIS',b'SONIC',b'CCMS'):
        hits=[hex(m.start()) for m in re.finditer(re.escape(kw),s[:0x2000])][:4]
        if hits: print(f'    {kw} @ {hits}')
    print()

# Also: is blob data == any of our decoded rom_pages?
print('=== compare blob0 data with decoded pages (swab both) ===')
import os
blob0=d[BLOBS[0]+0x10:BLOBS[0]+0x10+0x80000]
s0=swab(blob0)
PD='../SCC_extract/rom_pages'
for i in range(8):
    p=open(f'{PD}/page_{i:03d}.swab.bin','rb').read()
    hit=[j*0x10000 for j in range(8) if s0[j*0x10000:(j+1)*0x10000]==p]
    if hit: print(f'  page_{i:03d} found in blob0 at {[hex(x) for x in hit]}')
