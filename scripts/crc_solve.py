import struct, zlib, capstone

ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d=open(ROM,'rb').read()
def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

BLOBS=[(0x20f7000,0x80000,0x133c86ee,'S1'),(0x2197000,0x100000,0x8cc36740,'S2'),
       (0x2267000,0x200000,0xb90c90e6,'S3'),(0x2347000,0x300000,0xee53d172,'SK1'),
       (0x2367000,0x400000,0xdd685d7f,'b5'),(0x2377000,0x400000,0xabf1b23a,'b6')]

def crc32_custom(data,poly=0xEDB88320,init=0xFFFFFFFF,xor=0xFFFFFFFF):
    crc=init
    for b in data:
        crc^=b
        for _ in range(8):
            crc=(crc>>1)^poly if crc&1 else crc>>1
    return (crc^xor)&0xffffffff

# Solve CRC for S1 blob
base,sz,stored,name=BLOBS[0]
data=d[base+0x10:base+sz]
sw=swab(data)
print(f'=== solve CRC for {name}: stored=0x{stored:08x} ===')
cands={}
for label,buf in [('raw',data),('swab',sw)]:
    cands[f'crc32({label})']=zlib.crc32(buf)&0xffffffff
    cands[f'crc32~({label})']=(~zlib.crc32(buf))&0xffffffff
    cands[f'sum8({label})']=sum(buf)&0xffffffff
    cands[f'sum16be({label})']=sum(buf[i]<<8|buf[i+1] for i in range(0,len(buf)-1,2))&0xffffffff
    cands[f'sum16le({label})']=sum(buf[i]|buf[i+1]<<8 for i in range(0,len(buf)-1,2))&0xffffffff
    cands[f'xor8({label})']=0
    for x in buf: cands[f'xor8({label})']^=x
    for init in (0,0xFFFFFFFF):
        cands[f'crc32_{label}_i{init:x}']=crc32_custom(buf,init=init)
for k,v in cands.items():
    if v==stored: print('  MATCH',k,hex(v))
print('  closest scans done; sample:',{k:hex(v) for k,v in list(cands.items())[:6]})

# Verify blob linearity: disassemble S1 blob swab head as 68K
print('\n=== disassemble S1 blob swab head (68K) ===')
md=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_M68K_000)
for ins in md.disasm(sw[:64],0):
    print(f'  {ins.address:04x} {ins.bytes.hex():<10} {ins.mnemonic} {ins.op_str}')

# Compare: decoded pages 0..7 (S1 region?) with blob data at 0..0x80000
print('\n=== find decoded pages in S1 blob swab at expected offsets ===')
for i in range(8):
    p=open(f'../SCC_extract/rom_pages/page_{i:03d}.swab.bin','rb').read()
    pos=sw.find(p[:0x100])
    print(f'  page{i} @ blob swab 0x{pos:x}' if pos>=0 else f'  page{i} not found')
