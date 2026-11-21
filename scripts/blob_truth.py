import struct,re,capstone,zlib

ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d=open(ROM,'rb').read()
def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

BLOBS=[(0x20f7000,0x80000,'S1'),(0x2197000,0x100000,'S2'),(0x2267000,0x200000,'S3'),
       (0x2347000,0x300000,'SK1'),(0x2357000,0x300000,'SK2'),(0x2367000,0x400000,'b5'),(0x2377000,0x400000,'b6')]

print('=== search ESAG / SEGA in blob RAW and SWAB (first 0x2000) ===')
for base,sz,name in BLOBS:
    raw=d[base:base+min(sz,0x2000)]
    sw=swab(raw)
    res=[]
    for label,buf in (('raw',raw),('sw',sw)):
        for kw in (b'ESAG',b'SEGA',b'SONIC',b'GNISEC'):
            n=buf.count(kw)
            if n: res.append(f'{label}:{kw.decode()}x{n}@{hex(buf.find(kw))}')
    print(f'  {name} @{base:x}: {res}')

print()
print('=== blob data entropy check (is it compressed?) ===')
for base,sz,name in BLOBS[:3]:
    data=d[base+0x10:base+min(sz,0x10000)]
    # compressed data tends to have high entropy and few 0x00/0xFF runs
    import collections
    c=collections.Counter(data)
    print(f'  {name}: distinct={len(c)} top5={[(hex(k),v) for k,v in c.most_common(5)]}')

print()
print('=== try LZ77 decompress blob data (0x11 header?) ===')
def lzdec(src,size=0x10000):
    if src[0] not in (0x10,0x11): return None
    out=bytearray();win=bytes(65536);sp=4;W=len(win)
    while len(out)<size and sp<len(src):
        fl=src[sp];sp+=1
        for b in range(7,-1,-1):
            if len(out)>=size:break
            if fl&(1<<b):
                if sp+1>=len(src):return None
                b0,b1=src[sp],src[sp+1];sp+=2
                L=(b0>>4)+3;D=(((b0&0xf)<<8)|b1)+1
                si=W+len(out)-D
                if si<0:return None
                for k in range(L):
                    if len(out)>=size:break
                    j=si+k;out.append(win[j] if j<W else out[j-W])
            else:
                if sp>=len(src):return None
                out.append(src[sp]);sp+=1
    return bytes(out) if len(out)==size else None
for base,sz,name in BLOBS[:3]:
    r=lzdec(d[base+0x10:base+0x10+0x20000])
    print(f'  {name}: lzdec={"OK head="+r[:16].hex() if r else "FAIL"}')
