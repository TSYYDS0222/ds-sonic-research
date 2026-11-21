import struct, zlib

ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d=open(ROM,'rb').read()

BLOBS=[(0x20f7000,0x80000,0x133c86ee),(0x2197000,0x100000,0x8cc36740),
       (0x2267000,0x200000,0xb90c90e6),(0x2347000,0x300000,0xee53d172),
       (0x2357000,0x300000,0xbe1ed124),(0x2367000,0x400000,0xdd685d7f),
       (0x2377000,0x400000,0xabf1b23a)]

print('=== blob CRC hypothesis tests ===')
for base,sz,crc in BLOBS:
    tests={}
    # A: crc32 of data after 16-byte header
    tests['crc32(data@+0x10,sz-0x10)']=zlib.crc32(d[base+0x10:base+sz])&0xffffffff
    # B: crc32 of whole blob incl header except crc field
    tests['crc32(+4..sz)']=zlib.crc32(d[base+4:base+sz])&0xffffffff
    # C: crc32 of data after 0x10, full sz bytes
    tests['crc32(+0x10,sz)']=zlib.crc32(d[base+0x10:base+0x10+sz])&0xffffffff
    # D: sum words
    tests['sum16']=sum(d[i]<<8|d[i+1] for i in range(base+0x10,base+sz-1,2))&0xffffffff
    match=[k for k,v in tests.items() if v==crc]
    print(f'blob@{base:08x} stored={crc:08x} match={match}')
    if not match:
        print('   ',{k:hex(v) for k,v in tests.items()})
