import struct, re, os, sys

ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
OUT='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/rom_pages'
os.makedirs(OUT,exist_ok=True)
d=open(ROM,'rb').read(); GP=0x20b6000; p=d[GP:GP+5355024]
recs=[struct.unpack_from('<II',p,8+8*i) for i in range(128)]
ZERO=bytes(65536)

def dec(src, win=ZERO):
    out=bytearray(); sp=4; L=0; W=len(win); nsrc=len(src)
    while L<0x10000 and sp<nsrc:
        fl=src[sp]; sp+=1
        for b in range(7,-1,-1):
            if L>=0x10000: break
            if fl&(1<<b):
                if sp+1>=nsrc: return None,('eof2',L,sp)
                b0=src[sp]; b1=src[sp+1]; sp+=2
                n=(b0>>4)+3; D=(((b0&0xf)<<8)|b1)+1
                si=W+L-D
                if si<0: return None,('disp',L,D)
                for k in range(n):
                    if L>=0x10000: break
                    j=si+k
                    out.append(win[j] if j<W else out[j-W]); L+=1
            else:
                if sp>=nsrc: return None,('eof3',L,sp)
                out.append(src[sp]); sp+=1; L+=1
    if L<0x10000: return None,('short',L,sp,nsrc)
    return bytes(out),('ok',sp,nsrc)

pages=[]
for i,(o,s) in enumerate(recs):
    blob=p[o-GP:o-GP+s]
    if s==0x10000:
        r=blob[:0x10000]; st=('raw',)
    else:
        r,st=dec(blob)
        if r is None:
            print(f'{i:3d} FAIL {st}',flush=True); r=bytes(0x10000)
    pages.append(r)
    open(f'{OUT}/page_{i:03d}.bin','wb').write(r)

img=b''.join(pages)
open(f'{OUT}/rom_linear.bin','wb').write(img)
print('decoded',len(pages),'pages',flush=True)
for kw in (b'SEGA',b'ESAG',b'SONIC THE HEDGEHOG',b'MEGA DRIVE',b'GENESIS'):
    hits=[m.start() for m in re.finditer(re.escape(kw),img)]
    print(kw,len(hits),[hex(h) for h in hits[:12]])
print('page0 head',img[:32].hex())
print('at 0x100',img[0x100:0x110])
