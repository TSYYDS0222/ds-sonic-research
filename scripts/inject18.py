"""正确注入: 改 @0x5C0 表 slot2(Sonic3) 段 48-79, LZ77 压缩 MK 32 页."""
import struct, sys
sys.path.insert(0, '.')
from lz77_fast import encode

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
    page = swab(mk[i*0x10000:(i+1)*0x10000])
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

# 也同步改 @0x8 表对应项? @0x8 是运行时页表 - 断点证实游戏加载走 @0x5C0.
# 但 68K 取指走 @0x8 (page map). 为保险, 把 @0x8 的 page 0..31 也指向新 LZ 块
# (slot2 的 68K 地址空间 0x000000..0x1fffff -> page 0..31)
for i, (addr, size) in enumerate(entries):
    struct.pack_into('<II', nds, GP + 8 + 8*i, addr, size)

# 游戏名不改(避免破坏). 用户需在游戏列表选第3个(Sonic3)槽
out = 'C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms/MK_v18_real.nds'
open(out, 'wb').write(nds)
print('wrote', out, len(nds))

# 验证: 从 @0x8 和 @0x5c0 解压 page0 应为 MK 头
def dec(src):
    sz = src[1]|src[2]<<8|src[3]<<16; p=4; out=bytearray()
    while len(out)<sz and p<len(src):
        fl=src[p];p+=1
        for b in range(7,-1,-1):
            if len(out)>=sz: break
            if fl&(1<<b):
                b0=src[p];b1=src[p+1];p+=2
                n=(b0>>4)+3; D=(((b0&0xf)<<8)|b1)+1
                si=0x10000+len(out)-D
                for k in range(n):
                    if len(out)>=sz: break
                    j=si+k
                    out.append(0 if j<0 else (out[j-0x10000] if j>=0x10000 else 0))
            else:
                out.append(src[p]);p+=1
    return bytes(out)

for tblname, tbl in [('@0x8', GP+8), ('@0x5c0[48]', T5C0+8*48)]:
    a,s = struct.unpack_from('<II', nds, tbl)
    r = dec(nds[a:a+s])
    orig = swab(r)
    print(tblname, 'page0 SP/PC', orig[:8].hex(), 'header', orig[0x100:0x112])
