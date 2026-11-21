import struct, capstone

# Compare: original decoded Sonic pages vs standard MD ROM semantics
# Community note: emulator treats $Axxx/$Fxxx as $6xxx (opcode patch)
# Check what opcodes appear in decoded page_032 (Sonic2 header page)

p=open('../SCC_extract/rom_pages/page_032.swab.bin','rb').read()
md=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_M68K_000)

print('=== page_032 first 40 instructions (real ROM addr 0x20000) ===')
n=0
for ins in md.disasm(p[:0x100],0x20000):
    print(f'  {ins.address:06x} {ins.bytes.hex():<10} {ins.mnemonic:<8} {ins.op_str}')
    n+=1
    if n>=30:break

# Count opcodes with high nibble A or F in first 4KB
cntA=cntF=0
for ins in md.disasm(p[:0x1000],0):
    op=struct.unpack_from('>H',ins.bytes,0)[0] if len(ins.bytes)>=2 else 0
    hi=(op>>12)&0xf
    if hi==0xa:cntA+=1
    if hi==0xf:cntF+=1
print(f'\nopcodes starting $A: {cntA}, $F: {cntF} in first 4KB')

# Check Sonic3D source ROM
src=open('D:/tsyyds/shijiamoniqi2.11/Sonic 3D Blast (USA, Europe, Korea) (En).md','rb').read()
print('\n=== Sonic3D ROM header ===')
for i in range(0x0,0x20,4):
    print(f'  {i:04x}: {src[i:i+4].hex()}')
print('  @0x100:',src[0x100:0x120])
print('  SP={:08x} PC={:08x}'.format(*struct.unpack_from('>II',src,0)))
