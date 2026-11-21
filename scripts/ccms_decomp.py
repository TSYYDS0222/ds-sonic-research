import struct, re

d=open('D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds','rb').read()
def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

# S2 CCMS blob - is the data section itself LZ-compressed with a header?
b2=d[0x2197000+0x10:0x2197000+0x100000]
print('S2 blob data first 64:',b2[:64].hex())
print('as u32:',['%08x'%x for x in struct.unpack_from('<16I',b2,0)])

# Check: blob content between two similar blobs (0x2197000 and 0x2367000)
b5=d[0x2367000+0x10:0x2367000+0x400000]
same=sum(1 for i in range(0x10000) if b2[i]==b5[i])
print(f'\nb2 vs b5 first 64K identical bytes: {same}/65536')

# Maybe CCMS blob is the DECODED rom but byte-swapped differently (word vs dword)
p32=open('../SCC_extract/rom_pages/page_032.swab.bin','rb').read()
# page32 = ROM page0 (has header). Does its content appear anywhere in b2 (any transform)?
sig=p32[0x49:0x49+16]  # SEGA string
print('\nsig',sig)
for name,buf in [('b2raw',b2),('b2sw',swab(b2))]:
    print(f'  in {name}: {hex(buf.find(sig))}')
    # dword-swap sig
    s2=b''.join(sig[i:i+4][::-1] for i in range(0,len(sig),4))
    print(f'  dwapsig in {name}: {hex(buf.find(s2))}')

# What if CCMS blob is a ROM with 6-byte header offset - search SEGA in swab with broader window
b2sw=swab(b2)
for kw in (b'SEGA',b'SEG',b'1992',b'HEDGEHOG'):
    print(f'  {kw} in b2sw: {[hex(m.start()) for m in re.finditer(re.escape(kw),b2sw)][:5]}')
