"""只在指定原始块注入 MK，用于定位默认游戏实际使用哪个 @0x5C0 块。"""
import struct, sys
sys.path.insert(0, 'C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/work')
from lz_ccms import encode, decode

name = sys.argv[1]
BLOCKS = {'A': (0, 32), 'B': (32, 16), 'C': (48, 32), 'D': (80, 24)}
base, count = BLOCKS[name]
NDS = 'D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MK = 'D:/Users/江口小学/mortal-kombat.md'
GP = 0x20B6000; T5C0 = GP + 0x5C0; DATA = 0x19F1000

nds = bytearray(open(NDS, 'rb').read())
mk = bytearray(open(MK, 'rb').read().ljust(0x200000, b'\xff'))
def swab(b): return bytes(x for p in zip(b[1::2], b[0::2]) for x in p)

ptr = DATA; pages = []
for i in range(count):
    page = swab(bytes(mk[i * 0x10000:(i + 1) * 0x10000]))
    comp = encode(page)
    assert decode(comp, 0x10000) == page
    nds[ptr:ptr + len(comp)] = comp
    pages.append((ptr, len(comp))); ptr += len(comp)
for i, (a, s) in enumerate(pages):
    struct.pack_into('<II', nds, T5C0 + 8 * (base + i), a, s)

out = f'C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms/MK_probe_block{name}.nds'
open(out, 'wb').write(nds)
print(out)
