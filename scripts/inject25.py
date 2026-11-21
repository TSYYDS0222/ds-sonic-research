"""v25: 按真实 4 个游戏块的页数量正确全槽覆盖 MK。

原始 @0x5C0 表实际块布局（共 104 项）：
  block A: 0..31   (32 pages)
  block B: 32..47  (16 pages)
  block C: 48..79  (32 pages)  <- 默认居中选中（Sonic1 封面）
  block D: 80..103 (24 pages)

v24 错误地把每个块都当成 32 页连续写，导致默认块 48..79 拿到
MK page16..31 + page0..15 的乱序镜像，启动直接黑屏。
"""
import struct, sys
sys.path.insert(0, 'C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/work')
from lz_ccms import encode, decode

NDS = 'D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MK = 'D:/Users/江口小学/mortal-kombat.md'
GP = 0x20B6000
T5C0 = GP + 0x5C0
DATA = 0x19F1000
BLOCKS = [(0, 32), (32, 16), (48, 32), (80, 24)]

nds = bytearray(open(NDS, 'rb').read())
mk = bytearray(open(MK, 'rb').read().ljust(0x200000, b'\xff'))

def swab(b):
    return bytes(x for p in zip(b[1::2], b[0::2]) for x in p)

# v22 实测可用的版本不做 opcode 补丁
ptr = DATA
pages = []
for i in range(32):
    page = swab(bytes(mk[i * 0x10000:(i + 1) * 0x10000]))
    comp = encode(page)
    assert decode(comp, 0x10000) == page
    nds[ptr:ptr + len(comp)] = comp
    pages.append((ptr, len(comp)))
    ptr += len(comp)
print('compressed bytes', hex(ptr - DATA))

for base, count in BLOCKS:
    for i in range(count):
        addr, size = pages[i]
        struct.pack_into('<II', nds, T5C0 + 8 * (base + i), addr, size)

out = 'C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms/MK_v25_allblocks.nds'
open(out, 'wb').write(nds)
print('wrote', out)

# 验证默认块 48 指向 MK page0
a, s = struct.unpack_from('<II', nds, T5C0 + 8 * 48)
r = decode(nds[a:a + s], 0x10000)
print('entry48 decoded first bytes', swab(r)[:16].hex())
