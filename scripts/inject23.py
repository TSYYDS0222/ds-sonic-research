"""v23 = v22 + opcode 补丁: 高nibble A/E/F -> 6 (社区报告合集如此解释)."""
import struct, sys
sys.path.insert(0,'.')
from lz_ccms import encode, decode

NDS='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MK='D:/Users/江口小学/mortal-kombat.md'
GP=0x20b6000; T5C0=GP+0x5c0; DATA=0x19f1000
nds=bytearray(open(NDS,'rb').read())
mk=bytearray(open(MK,'rb').read().ljust(0x200000,b'\xff'))
def swab(b):return bytes(x for p in zip(b[1::2],b[0::2]) for x in p)
# opcode 补丁: 只在每页前 0x8000 (代码区常见) 做? 先做全文 A/E/F->6
n=0
for i in range(0,len(mk)-1,2):
    hi=mk[i]>>4
    if hi in (0xA,0xE,0xF):
        mk[i]=(0x6<<4)|(mk[i]&0xf); n+=1
print('patched words',n)
ptr=DATA;entries=[]
for i in range(32):
    page=swab(bytes(mk[i*0x10000:(i+1)*0x10000]))
    comp=encode(page); assert decode(comp,0x10000)==page
    nds[ptr:ptr+len(comp)]=comp;entries.append((ptr,len(comp)));ptr+=len(comp)
for i,(a,s) in enumerate(entries):struct.pack_into('<II',nds,T5C0+8*(48+i),a,s)
out='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms/MK_v23_opcode.nds'
open(out,'wb').write(nds);print('wrote',out)
