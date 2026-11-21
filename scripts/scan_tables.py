import struct
d=open('../SCC_extract/files/Game.pak','rb').read()
GP=0x20b6000
# 扫描 pak 头部 0..0x51000，找连续 >=16 个 {abs_rom_addr, size} 且 addr 落在数据区
DATA_LO=GP+0x51000; DATA_HI=GP+len(d)
print('data range',hex(DATA_LO),hex(DATA_HI))
runs=[]; i=8
while i<0x51000-8:
    a,b=struct.unpack_from('<II',d,i)
    if DATA_LO<=a<DATA_HI and (b==0x10000 or 0x100<=b<=0x20000):
        j=i; n=0
        while j<0x51000-8:
            a2,b2=struct.unpack_from('<II',d,j)
            if DATA_LO<=a2<DATA_HI and (b2==0x10000 or 0x100<=b2<=0x20000):
                n+=1;j+=8
            else: break
        if n>=16:
            runs.append((i,n)); i=j; continue
    i+=4
print('table-like runs (offset,count):')
for o,n in runs:
    print(f'  +0x{o:05x}  count={n}')
