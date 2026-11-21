import struct
ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d=open(ROM,'rb').read()
GP=0x20b6000; GPSZ=5355024
p=d[GP:GP+GPSZ]
print('pak len',hex(len(p)))
print('u32[0]=',hex(struct.unpack_from('<I',p,0)[0]),'u32[1]=',hex(struct.unpack_from('<I',p,4)[0]))

# 128 records at +8
recs=[struct.unpack_from('<II',p,8+8*i) for i in range(128)]
minoff=min(o for o,s in recs)
print('min rec off',hex(minoff),'as abs',hex(minoff),'rel to GP',hex(minoff-GP))
# determine if offset absolute or relative
print('first 8 recs:')
for i in range(8):
    o,s=recs[i]
    print(f'{i:3d} off={hex(o)} rel={hex(o-GP)} size={hex(s)} datahead={p[o-GP:o-GP+8].hex()}')

# map: for each rec unique offset
uniq=sorted(set(o for o,s in recs))
print('unique offsets',len(uniq))
# where does header data end / data begin
dstart=min(o-GP for o,s in recs)
print('data start rel',hex(dstart),'abs',hex(GP+dstart))
print('bytes before data start:',p[:dstart].count(0),'zeros of',hex(dstart))

# check recs identity pattern i vs i+64
print('\ni vs i+64:')
for i in range(64):
    o0,s0=recs[i]; o1,s1=recs[i+64]
    if o0!=o1 or s0!=s1:
        print(f' i={i} rec[{i}]={hex(o0)},{hex(s0)} rec[{i+64}]={hex(o1)},{hex(s1)}')
print('(only differences shown)')

# compressed vs raw classification
raw=[i for i,(o,s) in enumerate(recs) if s==0x10000]
comp=[i for i,(o,s) in enumerate(recs) if s!=0x10000]
print('\nraw pages',len(raw),'compressed',len(comp))
print('raw idx first30',raw[:30])
# stub sizes
from collections import Counter
print('size histogram',Counter(s for o,s in recs).most_common(12))
