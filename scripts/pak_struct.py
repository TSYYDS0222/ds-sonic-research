import struct, re

BASE='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
GP=0x20b6000
d=open(BASE,'rb').read()
pak=d[GP:GP+0x51b610]

print('=== game name strings in pak header (<0x10000) ===')
for kw in [b'SONIC',b'KNUCKLES',b'THE HEDGEHOG',b'3D',b'CHAOX']:
    for m in re.finditer(re.escape(kw),pak[:0x2000]):
        print(f'  {kw.decode():14s} @pak+0x{m.start():x}  {pak[m.start():m.start()+32]!r}')

print()
print('=== descriptor parse: 6 slots @ pak+0x410, step 0x3C ===')
for g in range(6):
    b=0x410+g*0x3c
    print(f'--- slot {g} @pak+0x{b:x} ---')
    for i in range(0,0x3c,4):
        v=struct.unpack_from('<I',pak,b+i)[0]
        print(f'  +{i:02x}: {v:08x}  ({v})', end='')
        # ascii if looks like ptr to string
        if 0x20b6000<=v<0x25d1610:
            so=v-GP
            print('  ->',repr(pak[so:so+24]),end='')
        print()

print()
print('=== find all 128-entry tables: scan for runs of valid {addr,size} ===')
DLO=GP+0x10000; DHI=GP+0x51b610
def valid(i):
    a,s=struct.unpack_from('<II',pak,i)
    return DLO<=a<DHI and (s==0x10000 or 0x100<=s<=0x20000)
for base in range(0,0x1000,4):
    if all(valid(base+8*k) for k in range(4)):
        # count run
        n=0
        while base+8*n+8<=len(pak) and valid(base+8*n): n+=1
        if n>=8:
            print(f'  table @pak+0x{base:x}: {n} consecutive valid entries')
