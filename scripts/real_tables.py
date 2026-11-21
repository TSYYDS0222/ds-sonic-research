import struct

BASE='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
GP=0x20b6000
d=open(BASE,'rb').read()
pak=d[GP:GP+0x51b610]

# correct descriptor step 0x48, CRC at +8, size at +c
print('=== correct descriptors (step 0x48) ===')
for g in range(6):
    b=0x410+g*0x48
    crc,size=struct.unpack_from('<II',pak,b+8)
    print(f'desc{g} @0x{b:x}: crc={crc:08x} size={size:08x}')
    # dump all words
    words=[struct.unpack_from('<I',pak,b+i)[0] for i in range(0,0x48,4)]
    print('   ',[f'{w:08x}' for w in words])

# The base addresses seen in descriptors
bases=[0x20f7000,0x2197000,0x2267000,0x2347000,0x2367000,0x2377000]
print()
print('=== dump at each game base (first 16 entries as {addr,size}) ===')
for base in bases:
    off=base-GP
    print(f'--- base 0x{base:x} = pak+0x{off:x} ---')
    for i in range(8):
        a,s=struct.unpack_from('<II',pak,off+8*i)
        print(f'  [{i}] {a:08x} {s:08x}', '  RAW:',pak[off+8*i:off+8*i+16].hex())
