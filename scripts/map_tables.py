import struct

ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d=open(ROM,'rb').read()
GP=0x20b6000

BLOBS=[(0x20f7000,0x80000,'S1'),(0x2197000,0x100000,'S2'),(0x2267000,0x200000,'S3'),
       (0x2347000,0x300000,'SK1'),(0x2357000,0x300000,'SK2'),(0x2367000,0x400000,'b5'),
       (0x2377000,0x400000,'b6')]

def which_blob(a):
    for s,e,n in BLOBS:
        if s<=a<e: return n
    return '?'

print('=== table @0x8 : addr -> which blob ===')
for tbl in (0x8,0x5c0):
    print(f'--- tbl 0x{tbl:x} ---')
    from collections import Counter
    c=Counter()
    for i in range(128):
        a,s=struct.unpack_from('<II',d,GP+tbl+8*i)
        c[which_blob(a)]+=1
    print('  distribution:',dict(c))
    print('  first 12:',[(i,hex(struct.unpack_from('<I',d,GP+tbl+8*i)[0]),which_blob(struct.unpack_from('<I',d,GP+tbl+8*i)[0])) for i in range(12)])
    print('  raw entries 100-110:',[(i,'%08x %08x'%struct.unpack_from('<II',d,GP+tbl+8*i)) for i in range(100,110)])

print()
print('=== descriptor base pointers vs table addr ranges ===')
DESC=[]
for g in range(6):
    db=GP+0x410+g*0x48
    size=struct.unpack_from('<I',d,db+0xc)[0]
    base=struct.unpack_from('<I',d,db+0x2c)[0]
    DESC.append((g,size,base))
    print(f'  g{g}: size={size:08x} base={base:08x} ({which_blob(base)})')

# Check: does each table's 128 entries fall inside exactly one game's blob?
print()
print('=== group table entries by descriptor base range ===')
for g,size,base in DESC:
    for tbl in (0x8,0x5c0):
        cnt=0
        for i in range(128):
            a,s=struct.unpack_from('<II',d,GP+tbl+8*i)
            if base<=a<base+size: cnt+=1
        if cnt: print(f'  desc g{g} base={base:x}: tbl{tbl:x} has {cnt} entries inside')
