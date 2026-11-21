import struct
d=open('D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds','rb').read()
def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

b2sw=swab(d[0x2197000+0x10:0x2197000+0x100000])
p32=open('../SCC_extract/rom_pages/page_032.swab.bin','rb').read()  # ROM page 0

# Hypothesis: CCMS blob = ROM with first N bytes removed
# find where CCMS blob's first 32 bytes appear in decoded ROM pages
sig=b2sw[:32]
allrom=bytearray()
for i in range(16):
    p=f'../SCC_extract/rom_pages/page_{i:03d}.swab.bin'
    import os
    if os.path.exists(p): allrom+=open(p,'rb').read()
pos=bytes(allrom).find(sig)
print(f'CCMS blob first 32 bytes found in decoded ROM at offset: 0x{pos:x}' if pos>=0 else 'NOT FOUND in decoded pages')

# Reverse: does decoded page0 content appear in CCMS blob at some offset?
# page0 signature from its code region
for off in (0x200,0x206,0x400,0x100):
    sig2=p32[off:off+16]
    p=b2sw.find(sig2)
    if p>=0: print(f'decoded page0[0x{off:x}] appears in CCMS blob @0x{p:x}')

# header bytes of decoded page0 and CCMS blob
print('\ndecoded page0[0x200:0x220]:',p32[0x200:0x220].hex())
print('ccms blob[0:0x20]         :',b2sw[0:0x20].hex())

# Try: XOR CCMS blob with decoded page0 at aligned offsets - look for constant XOR key
xor=b2sw[:0x100] if False else bytes(a^b for a,b in zip(b2sw[:0x100],p32[:0x100]))
from collections import Counter
print('\nXOR byte histogram first 0x100:',Counter(xor).most_common(8))
