"""最终注入: 修正的 lz_ccms 编码器 + swab + @0x5C0 slot2 段."""
import struct, sys
sys.path.insert(0, '.')
from lz_ccms import encode, decode

NDS = 'D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MK  = 'D:/Users/江口小学/mortal-kombat.md'
GP  = 0x20b6000
T5C0 = GP + 0x5c0
DATA = 0x19f1000
S2_START, S2_N = 48, 32

nds = bytearray(open(NDS,'rb').read())
mk = open(MK,'rb').read().ljust(0x200000, b'\xff')
def swab(b): return bytes(x for p in zip(b[1::2],b[0::2]) for x in p)

ptr = DATA; entries = []
for i in range(S2_N):
    page = swab(mk[i*0x10000:(i+1)*0x10000])   # 解压结果需为 swab 形式
    comp = encode(page)
    assert decode(comp,0x10000)==page
    nds[ptr:ptr+len(comp)] = comp
    entries.append((ptr,len(comp))); ptr += len(comp)
print('compressed',hex(ptr-DATA))
for i,(addr,size) in enumerate(entries):
    struct.pack_into('<II', nds, T5C0+8*(S2_START+i), addr, size)
out='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms/MK_v22_final.nds'
open(out,'wb').write(nds)
print('wrote',out)
# 验证 page0
a,s=entries[0]
r=decode(nds[a:a+s],0x10000)
orig=swab(r)
print('page0 real ROM: SP/PC',orig[:8].hex(),'hdr',orig[0x100:0x112])
