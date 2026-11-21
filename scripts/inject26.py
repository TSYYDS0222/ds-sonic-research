"""v26: 修正版注入——写真正被默认游戏读取的第二个表 @0x20B6840。

关键发现：Game.pak 里其实有两张连续的 {addr,size} 表：
  T1 @0x20B65C0，80 项（编号 0..79）
  T2 @0x20B6840，24 项（编号 80..103，之前被误当成 T1 尾部）
运行时解压器实测第一页来自 T2[8]（文件偏移 0x20B6880），
所以默认居中游戏读取的是 T2[8..23] 共 16 页。
v22 改 T1[48..79]（错误表），v25 把 MK page8.. 写进 T2[8]（页序错乱）。
v26：T2[8..23] = MK page0..15；T2[0..7] 也放 page0..7 兜底。
"""
import struct, sys
sys.path.insert(0, 'C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/work')
from lz_ccms import encode, decode

NDS = 'D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MK = 'D:/Users/江口小学/mortal-kombat.md'
GP = 0x20B6000
T2 = GP + 0x840          # 0x20B6840 真正的第二张表
DATA = 0x19F1000

nds = bytearray(open(NDS, 'rb').read())
mk = bytearray(open(MK, 'rb').read().ljust(0x200000, b'\xff'))
def swab(b): return bytes(x for p in zip(b[1::2], b[0::2]) for x in p)

ptr = DATA; pages = []
for i in range(24):
    page = swab(bytes(mk[i * 0x10000:(i + 1) * 0x10000]))
    comp = encode(page)
    assert decode(comp, 0x10000) == page
    nds[ptr:ptr + len(comp)] = comp
    pages.append((ptr, len(comp))); ptr += len(comp)
print('compressed bytes', hex(ptr - DATA))

# T2[8..23] = MK page0..15（默认游戏）；T2[0..7] = MK page0..7（兜底）
for i in range(8):
    a, s = pages[i]
    struct.pack_into('<II', nds, T2 + 8 * i, a, s)
for i in range(16):
    a, s = pages[i]
    struct.pack_into('<II', nds, T2 + 8 * (8 + i), a, s)

out = 'C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms/MK_v26_realtable.nds'
open(out, 'wb').write(nds)
print('wrote', out)
a, s = struct.unpack_from('<II', nds, T2 + 8 * 8)
print('T2[8]', hex(a), hex(s), 'decoded', swab(decode(nds[a:a + s], 0x10000))[:16].hex())
