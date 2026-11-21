"""正确注入: 改 @0x5C0 表 slot2(Sonic3) 段 48-79, LZ77 压缩 MK 32 页."""
import struct, sys
sys.path.insert(0, '.')
from lz_ccms import encode

NDS = 'D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MK  = 'D:/Users/江口小学/mortal-kombat.md'
GP  = 0x20b6000
T5C0 = GP + 0x5c0
DATA = 0x19f1000          # 7MB 空闲区起点
SLOT2_START, SLOT2_N = 48, 32   # @0x5C0 slot2 = 项48..79 (已由断点证实)

nds = bytearray(open(NDS, 'rb').read())
mk = open(MK, 'rb').read().ljust(0x200000, b'\xff')
assert len(mk) == 0x200000

def swab(b):
    return bytes(x for pr in zip(b[1::2], b[0::2]) for x in pr)

# 32 页, 每页 swab 后 LZ77 压缩
ptr = DATA
entries = []
for i in range(SLOT2_N):
    page = mk[i*0x10000:(i+1)*0x10000]
    comp = encode(page)
    assert comp[0] == 0x11 and (comp[1]|(comp[2]<<8)|(comp[3]<<16)) == 0x10000
    nds[ptr:ptr+len(comp)] = comp
    entries.append((ptr, len(comp)))
    ptr += len(comp)
    if ptr > 0x20b6000:
        raise RuntimeError('data overflow')

print('compressed total', hex(ptr-DATA), 'from', hex(DATA))

# 改 @0x5C0 表项 48..79 -> 新数据
for i, (addr, size) in enumerate(entries):
    struct.pack_into('<II', nds, T5C0 + 8*(SLOT2_START+i), addr, size)


out = 'C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms/MK_v21_ccmslz.nds'
open(out, 'wb').write(nds)
print('wrote', out, len(nds))
