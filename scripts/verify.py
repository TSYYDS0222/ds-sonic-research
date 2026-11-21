import struct, capstone, re
D='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/rom_pages'
md=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_M68K_000)

print('=== 各游戏区块起始页检查 (每32页=2MB) ===')
for base in (0,32,64,96):
    for i in range(base,min(base+4,128)):
        b=open(f'{D}/page_{i:03d}.swab.bin','rb').read()
        sp,pc=struct.unpack_from('>II',b,0)
        nonzero=sum(1 for x in b[:0x200] if x)
        # 从 PC 处反汇编(若在本页内)
        ins=[]
        if 0<pc<0xff00:
            for x in md.disasm(b[pc:pc+24],pc):
                ins.append(x.mnemonic+' '+x.op_str)
        print(f'page{i:3d} SP={sp:08x} PC={pc:08x} nz200={nonzero:3d} dis@pc={ins[:3]}')
    print()

print('=== page32 完整ROM头 (校验和域) ===')
b=open(f'{D}/page_032.swab.bin','rb').read()
print('0x00-0x20:',b[:0x20].hex())
print('0x100-0x120:',b[0x100:0x120].hex())
print('标题:',b[0x46:0x90])
