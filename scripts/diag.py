import struct, collections
ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d=open(ROM,'rb').read(); GP=0x20b6000; p=d[GP:GP+5355024]
recs=[struct.unpack_from('<II',p,8+8*i) for i in range(128)]

print('=== size distribution ===')
c=collections.Counter(s for o,s in recs)
print('raw(0x10000):',c[0x10000])
print('small sizes (<0x100):',[(i,hex(recs[i][0]-GP),recs[i][1]) for i in range(128) if recs[i][1]<0x100])
print()
print('=== duplicate offsets ===')
byoff=collections.defaultdict(list)
for i,(o,s) in enumerate(recs): byoff[o-GP].append(i)
for off,inds in sorted(byoff.items()):
    if len(inds)>1: print(hex(off),inds)
print('unique offsets',len(byoff),'of 128')
print()
print('=== compressed blob headers grouped by size ===')
for i,(o,s) in enumerate(recs):
    if s<0x100:
        q=p[o-GP:o-GP+s]
        print(f'{i:3d} off={o-GP:07x} sz={s:3d} data={q.hex()}')
