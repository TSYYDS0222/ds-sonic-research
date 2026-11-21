import struct, re

ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d=open(ROM,'rb').read(); GP=0x20b6000; p=d[GP:GP+5355024]
recs=[struct.unpack_from('<II',p,8+8*i) for i in range(128)]

def dec_page(src, window, L0=3, D0=1):
    """window = 之前所有输出的尾部 (bytes). 返回 (page_bytes, new_window, err)"""
    size=src[1]|src[2]<<8|src[3]<<16
    if size!=0x10000: return None,window,('hdr',hex(size))
    win=bytearray(window); out=bytearray(); sp=4
    while len(out)<size:
        if sp>=len(src): return None,window,('eof',len(out),sp,len(src))
        fl=src[sp]; sp+=1
        for b in range(7,-1,-1):
            if len(out)>=size: break
            if fl&(1<<b):
                if sp+1>=len(src): return None,window,('eof2',len(out))
                b0=src[sp]; b1=src[sp+1]; sp+=2
                L=(b0>>4)+L0; D=(((b0&0xf)<<8)|b1)+D0
                srcidx=len(win)+len(out)-D
                if srcidx<0: return None,window,('disp',len(out),D)
                for k in range(L):
                    if len(out)>=size: break
                    idx=srcidx+k
                    out.append(win[idx] if idx<len(win) else out[idx-len(win)])
            else:
                if sp>=len(src): return None,window,('eof3',len(out))
                out.append(src[sp]); sp+=1
    return bytes(out),(bytes(win)+bytes(out))[-0x10000:],('ok',sp,len(src))

def run(order_name, indices, win_init, reset=None):
    win=win_init; img=bytearray(65536*128); bad=[]
    for n,i in enumerate(indices):
        if reset and n%reset==0: win=win_init
        o,s=recs[i]; blob=p[o-GP:o-GP+s]
        if blob[:1] in (b'\x11',b'\x10'):
            r,win2,err=dec_page(blob,win)
            if r is None: bad.append((i,err)); r=bytes(65536); win=win2
            else: win=win2
        else: r=blob[:65536].ljust(65536,b'\0')
        img[i*65536:(i+1)*65536]=r
    img=bytes(img)
    hits={k:[hex(m.start()) for m in re.finditer(re.escape(k),img)][:8] for k in (b'SEGA',b'ESAG')}
    print(f'--- {order_name}: bad={len(bad)} first={bad[:3]}')
    print(f'    SEGA={hits[b"SEGA"]} ESAG={hits[b"ESAG"]}')
    return img

zero=b'\0'*0x10000
seq=list(range(128))
a=run('table order, carry64k', seq, zero)
b=run('table order, carry64k reset32', seq, zero, 32)
order=sorted(range(128), key=lambda i: recs[i][0])
c=run('offset order, carry64k', order, zero)

# 检查裸页里的 SEGA/ESAG
for i,(o,s) in enumerate(recs):
    if s==0x10000:
        q=p[o-GP:o-GP+s]
        if b'SEGA' in q or b'ESAG' in q:
            print('RAW page',i,'has SEGA/ESAG at', [hex(m.start()) for m in re.finditer(b'SEGA|ESAG',q)][:4])
