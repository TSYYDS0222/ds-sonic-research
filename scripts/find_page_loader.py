import struct, re, capstone

d=open('rom.bin','rb').read()
a9=d[0x4000:0x4000+537728]
base=0x2004000

# The 68K page table in RAM - from descriptor fields we saw 0x023d7008..0x023d7944
# Those are runtime RAM addresses. Find code that reads/writes around there.
# ARM literal loads: ldr rX,[pc,#imm] -> literal word = 0x023d7xxx
print('=== literal loads of 0x023d7xxx region ===')
hits=[]
for o in range(0,len(a9)-4,4):
    w=struct.unpack_from('<I',a9,o)[0]
    if 0x023d7000<=w<0x023d8000:
        hits.append((base+o,w))
print('count',len(hits))
for a,w in hits[:20]: print(f'  @{a:08x}: {w:08x}')

# Also search for the decompressor caller we found earlier (0x2004df4 decompress)
# and the function reading page-table entries {addr,size}. Look for 'ldr' pairs
# near ldrb loops. Search for references to 0x11 type check
print()
print('=== BL to decompressor 0x2004df4 callers context ===')
md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);md.skipdata=True
# disassemble around 0x2004bc0 caller we found
for ins in md.disasm(a9[0x2004bc0-base:0x2004c60-base],0x2004bc0):
    print(f'  {ins.address:08x} {ins.mnemonic:<7} {ins.op_str}')
