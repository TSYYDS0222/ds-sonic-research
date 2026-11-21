import struct
ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d=open(ROM,'rb').read()
GP=0x20b6000

# Known values to locate
SIZES=[0x80000,0x100000,0x200000,0x300000,0x400000,0x400000]
BASES=[0x20f7000,0x2197000,0x2267000,0x2347000,0x2367000,0x2377000]
CRCS=[0x11394d,0x1125fb,0x1193a5,0x11cdf9,0x1197b7,0x118daf]

print('=== locate each game descriptor: step 0x3c ===')
for g in range(6):
    b=0x410+g*0x3c
    print(f'slot{g} @pak+0x{b:x}:')
    for i in range(0,0x3c,4):
        v=struct.unpack_from('<I',d,GP+b+i)[0]
        tag=''
        if v==SIZES[g]: tag=' <== SIZE'
        if v==BASES[g]: tag=' <== BASE'
        if v==CRCS[g]: tag=' <== CRC'
        print(f'  +{i:02x} (0x{GP+b+i:x}): {v:08x}{tag}')
    print()

print('=== also dump 0x570..0x5c0 (possible slot6) ===')
for i in range(0x570,0x5c0,4):
    print(f'  0x{i:x}: {struct.unpack_from("<I",d,GP+i)[0]:08x}')
