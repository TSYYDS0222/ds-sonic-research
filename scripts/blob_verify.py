import struct, re

ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d=open(ROM,'rb').read()
def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

BLOBS=[(0x20f7000,0x80000,'Sonic1'),(0x2197000,0x100000,'Sonic2'),
       (0x2267000,0x200000,'Sonic3'),(0x2347000,0x300000,'S&K-a'),
       (0x2357000,0x300000,'S&K-b'),(0x2367000,0x400000,'blob5'),(0x2377000,0x400000,'blob6')]

for base,sz,name in BLOBS:
    data=d[base+0x10:base+sz]
    s=swab(data)
    print(f'=== {name} blob@{base:08x} size={sz:08x} ===')
    # ROM header should be at 0x100 in swabbed data
    print('  @0x100:',s[0x100:0x120])
    print('  SP/PC :',s[0:8].hex())
    for kw in (b'SEGA',b'GENESIS',b'SONIC',b'MEGA DRIVE',b'199'):
        hits=[hex(m.start()) for m in re.finditer(re.escape(kw),s[:0x1000])][:5]
        if hits: print(f'    {kw}: {hits}')
    print()

# Compare blob data vs decoded rom pages to find relationship
PD='../SCC_extract/rom_pages'
import os
print('=== match blob1 (Sonic2) vs decoded pages ===')
b1=swab(d[0x2197000+0x10:0x2197000+0x100000])
for i in range(16):
    p=open(f'{PD}/page_{i:03d}.swab.bin','rb').read()
    # blob starts at +0x10, so alignment offset differs; find p in b1
    idx=b1.find(p[:0x1000])
    if idx>=0: print(f'  page{i} @ blob+0x{idx:x}')
