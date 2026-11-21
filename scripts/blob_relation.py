import struct, zlib, os, re

ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d=open(ROM,'rb').read()
def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

PD='../SCC_extract/rom_pages'
pages=[]
for i in range(128):
    p=f'{PD}/page_{i:03d}.swab.bin'
    pages.append(open(p,'rb').read() if os.path.exists(p) else None)
print('pages available',sum(1 for p in pages if p))

# blob1 = Sonic2 @0x2197000, 1MB. Find which decoded pages appear in it
b1raw=d[0x2197000+0x10:0x2197000+0x100000]
b1sw=swab(b1raw)
print('\n=== search each decoded page signature in blob1 (raw and swab) ===')
hits=0
for i,p in enumerate(pages):
    if not p: continue
    sig=p[:0x40]
    a=b1sw.find(sig)
    b=b1raw.find(sig)
    if a>=0 or b>=0:
        print(f'  page{i}: swab@{hex(a)} raw@{hex(b)}')
        hits+=1
print('total hits',hits)

# Also: is blob1 raw actually one of the decompressed pages concatenated?
# Compare first 0x1000 of blob1 raw at every 0x10000 boundary with pages
print('\n=== blob1 64K-block boundaries vs pages ===')
for k in range(16):
    blk=b1raw[k*0x10000:(k+1)*0x10000]
    sw=swab(blk)
    m=[i for i,p in enumerate(pages) if p and p[:0x100]==sw[:0x100]]
    print(f'  block{k} @+0x{k*0x10000:x}: head={blk[:8].hex()} matchpages={m[:6]}')

# CRC hypothesis: crc32 over swabbed data
print('\n=== CRC over swab variants ===')
BLOBS=[(0x20f7000,0x80000,0x133c86ee),(0x2197000,0x100000,0x8cc36740),
       (0x2267000,0x200000,0xb90c90e6)]
for base,sz,crc in BLOBS:
    data=d[base+0x10:base+sz]
    sw=swab(data)
    tests={
        'crc32(sw)':zlib.crc32(sw)&0xffffffff,
        'crc32(raw)':zlib.crc32(data)&0xffffffff,
        'crc32(sw[0:sz-0x10])':zlib.crc32(sw)&0xffffffff,
        'adler32(sw)':zlib.adler32(sw)&0xffffffff,
    }
    print(f'blob@{base:x} stored={crc:08x}',{k:hex(v) for k,v in tests.items()})
