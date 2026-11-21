import struct, re, os
ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
OUT='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/rom_pages'
os.makedirs(OUT,exist_ok=True)
d=open(ROM,'rb').read(); GP=0x20b6000; p=d[GP:GP+5355024]
recs=[struct.unpack_from('<II',p,8+8*i) for i in range(128)]
ZERO=bytes(65536)

def dec(src, fill=0xff):
    out=bytearray(); sp=4; L=0; nsrc=len(src)
    while L<0x10000:
        if sp>=nsrc:
            out.extend(bytes([fill])*(0x10000-L)); break
        fl=src[sp]; sp+=1
        for b in range(7,-1,-1):
            if L>=0x10000: break
            if fl&(1<<b):
                if sp+1>=nsrc:
                    out.extend(bytes([fill])*(0x10000-L)); L=0x10000; break
                b0=src[sp]; b1=src[sp+1]; sp+=2
                n=(b0>>4)+3; D=(((b0&0xf)<<8)|b1)+1
                si=65536+L-D
                for k in range(n):
                    if L>=0x10000: break
                    j=si+k
                    out.append(ZERO[j] if j<65536 else out[j-65536]); L+=1
            else:
                if sp>=nsrc:
                    out.extend(bytes([fill])*(0x10000-L)); L=0x10000; break
                out.append(src[sp]); sp+=1; L+=1
    return bytes(out)

def sw(b):
    o=bytearray(len(b)); o[0::2]=b[1::2]; o[1::2]=b[0::2]; return bytes(o)

pages=[]
for i,(o,s) in enumerate(recs):
    blob=p[o-GP:o-GP+s]
    if s==0x10000: r=blob[:0x10000]
    else: r=dec(blob)
    r=sw(r)  # 16-bit byte swap -> 正确 68K 字节序
    pages.append(r)
    open(f'{OUT}/page_{i:03d}.swab.bin','wb').write(r)

img=b''.join(pages)
open(OUT+'/rom_all_8mb.swab.bin','wb').write(img)
print('pages',len(pages))
# 搜索标题及已知签名
for kw in (b'SEGA MEGA DRIVE',b'SEGA GENESIS',b'(C)SEGA',b'SONIC THE HEDGEHOG',b'KNUCKLES'):
    hits=[(m.start()//0x10000,m.start()%0x10000) for m in re.finditer(re.escape(kw),img)]
    print(kw.decode(),len(hits),hits[:20])
