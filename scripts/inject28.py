"""v28: 真实双表全槽版，按每个块的真实页数写 MK，不做 opcode 补丁。

T1 @0x20B65C0: [0..31]=32页, [32..47]=16页, [48..63]=16页, [64..79]=16页
T2 @0x20B6840: [0..7], [8..15], [16..23] 各 8 页（默认选中最后一组）
"""
import struct, sys
sys.path.insert(0, 'C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/work')
from lz_ccms import encode, decode

NDS = 'D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MK = 'D:/Users/江口小学/mortal-kombat.md'
GP = 0x20B6000
T1 = GP + 0x5C0
T2 = GP + 0x840
DATA = 0x19F1000

nds = bytearray(open(NDS, 'rb').read())
mk = open(MK, 'rb').read().ljust(0x200000, b'\xff')
def swab(b): return bytes(x for p in zip(b[1::2], b[0::2]) for x in p)

ptr = DATA; pages = []
for i in range(32):
    page = swab(mk[i * 0x10000:(i + 1) * 0x10000])
    comp = encode(page)
    assert decode(comp, 0x10000) == page
    nds[ptr:ptr + len(comp)] = comp
    pages.append((ptr, len(comp))); ptr += len(comp)
print('compressed bytes', hex(ptr - DATA))

blocks = [(T1, 0, 32), (T1, 32, 16), (T1, 48, 16), (T1, 64, 16),
          (T2, 0, 8), (T2, 8, 8), (T2, 16, 8)]
for table, base, count in blocks:
    for i in range(count):
        a, s = pages[i]
        struct.pack_into('<II', nds, table + 8 * (base + i), a, s)

out = 'C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms/MK_v28_realtable_all.nds'
open(out, 'wb').write(nds)
print('wrote', out)
