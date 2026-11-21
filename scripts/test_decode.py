import struct, re, sys

ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d=open(ROM,'rb').read(); GP=0x20b6000; p=d[GP:GP+5355024]
recs=[struct.unpack_from('<II',p,8+8*i) for i in range(128)]

def fwd(src, L0=3, D0=1, msb=True, outsz=0x10000):
    out=bytearray(); sp=0
    while len(out)<outsz:
        if sp>=len(src): return None,('eof',len(out))
        fl=src[sp]; sp+=1
        bits=range(7,-1,-1) if msb else range(8)
        for b in bits:
            if len(out)>=outsz: break
            if fl&(1<<b):
                if sp+1>=len(src): return None,('eof2',len(out))
                b0=src[sp]; b1=src[sp+1]; sp+=2
                L=(b0>>4)+L0; D=(((b0&0xf)<<8)|b1)+D0
                s=len(out)-D
                if s<0: return None,('disp',len(out),D)
                for k in range(L):
                    if len(out)>=outsz: break
                    out.append(out[s+k])
            else:
                if sp>=len(src): return None,('eof3',len(out))
                out.append(src[sp]); sp+=1
    return bytes(out),('ok',sp,len(src))

def rev(src, L0=3, D0=2, msb=True, outsz=0x10000):
    """从后往前解: 模拟 0x2004DF4, 头在前面, 数据区在 src"""
    out=bytearray(outsz); w=outsz; sp=len(src)
    while w>0:
        if sp<=0: return None,('eof',outsz-w)
        fl=src[sp-1]; sp-=1
        bits=range(7,-1,-1) if msb else range(8)
        for b in bits:
            if w<=0: break
            if fl&(1<<b):
                if sp<2: return None,('eof2',outsz-w)
                b0=src[sp-1]; b1=src[sp-2]; sp-=2
                L=(b0>>4)+L0; D=(((b0&0xf)<<8)|b1)+D0
                for k in range(L):
                    if w<=0: break
                    idx=w-1+D
                    if idx>=outsz: return None,('oob',outsz-w,D)
                    w-=1; out[w]=out[idx]
            else:
                if sp<1: return None,('eof3',outsz-w)
                w-=1; out[w]=src[sp-1]; sp-=1
    return bytes(out),('ok',sp)

def swab(b):
    return bytes(x for pair in zip(b[1::2],b[0::2]) for x in pair)

o,s=recs[0]; blob=p[o-GP:o-GP+s]
hdr,body=blob[:4],blob[4:]
variants={
 'fwd_d1':lambda: fwd(body,3,1)[0],
 'fwd_d2':lambda: fwd(body,3,2)[0],
 'fwd_lsb':lambda: fwd(body,3,1,False)[0],
 'rev_d1':lambda: rev(body,3,1)[0],
 'rev_d2':lambda: rev(body,3,2)[0],
 'rev_body_swap':lambda: rev(bytes(reversed(body)),3,2)[0],
 'fwd_bodyrev':lambda: fwd(bytes(reversed(body)),3,1)[0],
 'fwd_blobrev':lambda: fwd(bytes(reversed(blob)),3,1)[0],
 'fwd_swab':lambda: fwd(swab(body),3,1)[0],
}
for name,fn in variants.items():
    try: r=fn()
    except Exception as e: print(name,'EXC',e); continue
    if r is None: print(f'{name:16s} FAIL'); continue
    hits={k:[hex(m.start()) for m in re.finditer(re.escape(k),r)][:4] for k in (b'SEGA',b'ESAG')}
    print(f'{name:16s} len={len(r)} head={r[:24].hex()} SEGA={hits[b"SEGA"]} ESAG={hits[b"ESAG"]}')
