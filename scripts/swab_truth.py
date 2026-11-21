import struct, re

ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d=open(ROM,'rb').read()
def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

# decoded page with real ROM header
p32=open('../SCC_extract/rom_pages/page_032.swab.bin','rb').read()
print('page_032.swab header @+0x40:',p32[0x40:0x60])

# raw (pre-swab) version of same page
p32raw=open('../SCC_extract/rom_pages/page_032.bin','rb').read()
print('page_032.raw   header @+0x40:',p32raw[0x40:0x60])

# The CCMS blob S2 - swab vs raw, search for the S2 title signature
b2=d[0x2197000+0x10:0x2197000+0x100000]
print('\nS2 blob raw   @0x40:',b2[0x40:0x60])
print('S2 blob swab  @0x40:',swab(b2)[0x40:0x60])

# find title in decoded page 32, then search that exact byte pattern in blob raw/swab
title=b'SONIC THE HEDGEHOG 2'
toff=p32.find(title)
print(f'\ntitle in decoded page32 @0x{toff:x}')
if toff>=0:
    sig=p32[toff:toff+len(title)]
    print('  sig raw  (pre-swab page):',p32raw[toff:toff+len(title)])
    print('  found in b2 raw? ',hex(b2.find(sig)))
    print('  found in b2 swab?',hex(swab(b2).find(sig)))
    # swab sig
    ssig=swab(sig)
    print('  sig swabbed:',ssig)
    print('  swabbed sig in b2 raw?',hex(b2.find(ssig)))
