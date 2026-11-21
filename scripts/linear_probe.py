import struct,re

ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d=open(ROM,'rb').read()
def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

# blob1 = Sonic2. Its ROM header page should contain "SEGA" at ROM offset 0x100
# We know page_032.swab.bin has the Sonic2 header string at +0x49 (ROM addr 0x20049)
p32=open('../SCC_extract/rom_pages/page_032.swab.bin','rb').read()
print('page32 header region:',p32[0x40:0x60])

b1raw=d[0x2197000+0x10:0x2197000+0x100000]
b1sw=swab(b1raw)

# find the exact ROM header signature from page32 in blob1 swab
for sig_off in (0x40,0x46,0x49,0x100):
    sig=p32[sig_off:sig_off+0x20]
    pos=b1sw.find(sig)
    print(f'page32 sig@+0x{sig_off:x} -> blob1sw pos 0x{pos:x}' if pos>=0 else f'page32 sig@+0x{sig_off:x} not found')

# Search SEGA directly in blob1 swab (whole)
for m in re.finditer(b'SEGA',b1sw):
    print('SEGA in blob1sw @',hex(m.start()),b1sw[m.start()-8:m.start()+32])

# Key: maybe blob data itself is NOT swabbed and SEGA appears as ESAG
for m in re.finditer(b'ESAG',b1raw):
    print('ESAG in blob1raw @',hex(m.start()),b1raw[m.start()-8:m.start()+32])

# Determine relationship: take page32 full 64K, find in blob1 swab
pos=b1sw.find(p32)
print('full page32 in blob1sw @',hex(pos))
pos2=b1raw.find(p32)
print('full page32 in blob1raw @',hex(pos2))

# If found at offset X, then blob1 swab = ROM starting at some base
# ROM page32 means ROM offset 0x200000... but Sonic2 is 1MB so page32 belongs to another game
# Let's check which pages 0..15 (Sonic2's 1MB) are where
print('\n=== locate pages 0..16 in blob1sw ===')
for i in range(17):
    p=open(f'../SCC_extract/rom_pages/page_{i:03d}.swab.bin','rb').read()
    pos=b1sw.find(p[:0x200])
    if pos>=0: print(f'  page{i:3d} @ blob1sw+0x{pos:x} (= expected 0x{i*0x10000:x})')
