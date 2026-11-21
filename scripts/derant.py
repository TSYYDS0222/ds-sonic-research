import struct

ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d=open(ROM,'rb').read()
def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

# S2: CCMS blob at 0x2197000. Decoded pages 16-31 are S2's 1MB (pages 16..31)
# page_032 had SEGA header at +0x49 -> that's ROM offset 0x49?? means page 32 = ROM page 0!
# Actually page numbering: page_032.swab @+0x40 = "  (C)SEGA 1992.SEPSONIC THE " -> ROM header region
# So decoded page 32 == ROM page 0 (offset 0x00000-0x0FFFF)
p32=open('../SCC_extract/rom_pages/page_032.swab.bin','rb').read()
b2sw=swab(d[0x2197000+0x10:0x2197000+0x100000])

print('decoded page32 @0x40:',p32[0x40:0x60])
print('ccms swab      @0x40:',b2sw[0x40:0x60])
print()
# XOR analysis at same offsets
print('=== XOR decodedpage32 vs ccms-swab (first 0x40 bytes) ===')
for i in range(0,0x40,16):
    a=p32[i:i+16];b=b2sw[i:i+16]
    x=bytes(p^q for p,q in zip(a,b))
    print(f'  {i:04x}: dec={a.hex()} ccms={b.hex()} xor={x.hex()}')

# Try: maybe CCMS blob data == decoded pages but with byte rotation per byte
# Check if ccms[i] is a bit-rotation of decoded[i]
def rotations(x):
    return {((x<<k)|(x>>(8-k)))&0xff for k in range(8)}
match_rot=0
for i in range(0x100):
    if b2sw[i] in rotations(p32[i]): match_rot+=1
print(f'\nbit-rotation match in first 0x100: {match_rot}/256')

# Try byte-swap within 32-bit word (already swab done) - compare decoded page RAW vs ccms RAW
p32raw=open('../SCC_extract/rom_pages/page_032.bin','rb').read()
b2raw=d[0x2197000+0x10:0x2197000+0x100000]
match_direct=sum(1 for i in range(0x100) if p32raw[i]==b2raw[i])
print(f'direct match decoded.raw vs ccms.raw first 0x100: {match_direct}/256')
