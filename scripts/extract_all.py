import struct, os, re, capstone

ROM = 'D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
OUT = 'C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract'
d = open(ROM, 'rb').read()

A9OFF, A9SZ, A9BASE = 0x4000, 537728, 0x2004000
A7OFF, A7SZ, A7BASE = 0x87600, 175896, 0x2380000
a9 = d[A9OFF:A9OFF+A9SZ]

os.makedirs(OUT + '/files', exist_ok=True)
os.makedirs(OUT + '/emulator', exist_ok=True)

# ---------- 1. 文件系统 ----------
fnt_off, fat_off = 0xb2600, 0xb2800
fat = [(struct.unpack_from('<II', d, fat_off + 8*i)) for i in range(9)]
names = ['snd_Sonic1_sfx.mods', 'snd_Sonic1_trx.mods', 'snd_Sonic2_sfx.mods',
         'snd_Sonic2_trx.mods', 'snd_Sonic3_sfx.mods', 'snd_Sonic3_trx.mods',
         'title.wav', 'Game.pak', 'screensGame_us.dat']
manifest = []
for i, (s, e) in enumerate(fat):
    p = f'{OUT}/files/{names[i]}'
    open(p, 'wb').write(d[s:e])
    manifest.append(f'{names[i]}\t{s:#x}\t{e-s}')

# ---------- 2. 模拟器 ----------
open(f'{OUT}/emulator/arm9.bin', 'wb').write(a9)
open(f'{OUT}/emulator/arm7.bin', 'wb').write(d[A7OFF:A7OFF+A7SZ])

TB = 0x202F480
tbl = struct.unpack_from('<65536I', a9, TB - A9BASE)
open(f'{OUT}/emulator/m68k_dispatch_table.bin', 'wb').write(a9[TB-A9BASE:TB-A9BASE+0x40000])

uniq = sorted(set(tbl))
with open(f'{OUT}/emulator/m68k_handlers_unique.txt', 'w') as f:
    f.write('# 68K opcode handler entry points (unique), ARM mode\n')
    f.write(f'# base={TB:#010x}  entries=65536  unique={len(uniq)}\n')
    f.write(f'# code range {hex(min(uniq))} .. {hex(max(uniq))}  (span {max(uniq)-min(uniq)} bytes)\n')
    for a in uniq:
        f.write(f'{a:08X}\n')

with open(f'{OUT}/emulator/m68k_opcode_map.txt', 'w') as f:
    f.write('# opcode -> handler\n')
    cur = None
    for op, h in enumerate(tbl):
        if h != cur:
            f.write(f'{op:04X} {h:08X}\n')
            cur = h

md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
md.skipdata = True
with open(f'{OUT}/emulator/arm9_full.asm', 'w') as f:
    for i in md.disasm(a9, A9BASE):
        f.write(f'{i.address:08x}  {i.bytes.hex():<8} {i.mnemonic:<8} {i.op_str}\n')

# 关键处理器样本
samples = {'NOP_4E71': 0x4E71, 'RTS_4E75': 0x4E75, 'MOVEQ_7000': 0x7000,
           'JSR_absL_4EB9': 0x4EB9, 'BRA_S_60FE': 0x60FE, 'LINK_4E50': 0x4E50,
           'opcode0_ORI': 0x0000, 'illegal': 0x4AFC}
with open(f'{OUT}/emulator/key_handlers.asm', 'w') as f:
    for nm, op in samples.items():
        a = tbl[op]
        f.write(f'==== {nm}  opcode {op:04X} -> {a:08X}\n')
        for i in md.disasm(a9[a-A9BASE:a-A9BASE+64], a):
            f.write(f'  {i.address:08x}  {i.bytes.hex():<8} {i.mnemonic:<8} {i.op_str}\n')
        f.write('\n')

# ---------- 3. Game.pak ----------
GP, GPSZ = 0x020b6000, 5355024
pak = d[GP:GP+GPSZ]
recs = [struct.unpack_from('<II', pak, 8 + 8*i) for i in range(128)]
comp = sum(1 for o, s in recs if pak[o-GP] in (0x11, 0x10))
with open(f'{OUT}/emulator/game_pak_chunks.txt', 'w') as f:
    f.write(f'# Game.pak @ {GP:#x}  size={GPSZ}\n')
    f.write(f'# header: u32={struct.unpack_from("<I",pak,0)[0]}  u32={struct.unpack_from("<I",pak,4)[0]:#x}\n')
    f.write(f'# 128 records x 64KB dest; compressed={comp} raw={128-comp}\n')
    f.write('# idx  pak_offset   stored   firstbyte\n')
    for i, (o, s) in enumerate(recs):
        f.write(f'{i:3d} {o:#010x} {s:8d}  {pak[o-GP]:02x}\n')

open(f'{OUT}/files/_manifest.txt', 'w').write('\n'.join(manifest))
print('chunks compressed', comp, 'raw', 128-comp)
print('unique handlers', len(uniq))
print('done')
