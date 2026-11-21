"""v24: 把所有游戏槽的第一组页都指向 MK (覆盖所有可能的加载入口)."""
import struct,sys
sys.path.insert(0,'.')
from lz_ccms import encode,decode
NDS='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MK='D:/Users/江口小学/mortal-kombat.md'
GP=0x20b6000;T5C0=GP+0x5c0;DATA=0x19f1000
nds=bytearray(open(NDS,'rb').read())
mk=bytearray(open(MK,'rb').read().ljust(0x200000,b'\xff'))
def swab(b):return bytes(x for p in zip(b[1::2],b[0::2]) for x in p)
# opcode 补丁
for i in range(0,len(mk)-1,2):
    if (mk[i]>>4) in (0xA,0xE,0xF): mk[i]=(0x6<<4)|(mk[i]&0xf)
# 压缩 32 页
ptr=DATA;pages=[]
for i in range(32):
    p=swab(bytes(mk[i*0x10000:(i+1)*0x10000]));c=encode(p)
    nds[ptr:ptr+len(c)]=c;pages.append((ptr,len(c)));ptr+=len(c)
# 4 组游戏槽在 @0x5C0: 0-31,32-63,64-95,96-127(只104有效)
# 每组前 32 页都指向 MK 对应页 (循环)
for grp in range(4):
    base=grp*32
    if base>=104: continue
    for i,(a,s) in enumerate(pages):
        if base+i>=104: break
        struct.pack_into('<II',nds,T5C0+8*(base+i),a,s)
out='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms/MK_v24_allslots.nds'
open(out,'wb').write(nds);print('wrote',out)
