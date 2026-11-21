"""DS LZ77 type 0x11 encoder with 64KB zero-preset dictionary.
Format: [0x11][size 24-bit LE][tokens...]
tokens: flag byte (MSB first), 0=literal, 1=(len,disp) pair
  len = (b0>>4)+3, disp = (((b0&0xf)<<8)|b1)+1
  backref source = 0x10000 + outpos - disp   (64KB zero window prepended)
"""
import struct

def encode(data, winsize=0x10000):
    size=len(data)
    out=bytearray([0x11, size&0xff, (size>>8)&0xff, (size>>16)&0xff])
    # virtual output = zeros(winsize) + data. We match against this.
    pos=0
    flags=bytearray()
    nflag=0
    while pos<size:
        best_len=0; best_disp=0
        # max match length 18 (nibble +3, max 0xf+3=18)
        maxl=min(18, size-pos)
        if maxl>=3:
            # search window: last winsize bytes of (zeros+data)
            # abs position in virtual stream = winsize+pos
            vpos=winsize+pos
            lo=max(0, vpos-winsize)
            # try displacements 1..(vpos-lo), scan for longest match
            # limit search for speed
            hi_disp=min(vpos-lo, 0x1000)
            for disp in range(1, hi_disp+1):
                src=vpos-disp
                l=0
                while l<maxl:
                    a = 0 if src+l < winsize else data[src+l-winsize]
                    if a==data[pos+l]: l+=1
                    else: break
                if l>best_len:
                    best_len=l; best_disp=disp
                    if l>=maxl: break
        if best_len>=3:
            flags.append(1)
            b0=((best_len-3)<<4)|((best_disp-1)>>8)
            b1=(best_disp-1)&0xff
            out.append(b0); out.append(b1)
            pos+=best_len
        else:
            flags.append(0)
            out.append(data[pos])
            pos+=1
        nflag+=1
        if nflag==8:
            # flags will be inserted later; placeholder handled by rebuilding
            nflag=0
    return bytes(out), bytes(flags)

def encode2(data):
    """Correct flag interleaving."""
    size=len(data)
    out=bytearray([0x11,size&0xff,(size>>8)&0xff,(size>>16)&0xff])
    pos=0
    while pos<size:
        flag=0; tokens=bytearray()
        for bit in range(8):
            if pos>=size: break
            best_len=0;best_disp=0
            maxl=min(18,size-pos)
            if maxl>=3:
                vpos=0x10000+pos
                hi=min(vpos,0x1000)
                for disp in range(1,hi+1):
                    src=vpos-disp;l=0
                    while l<maxl:
                        a=0 if src+l<0x10000 else data[src+l-0x10000]
                        if a==data[pos+l]:l+=1
                        else:break
                    if l>best_len:
                        best_len=l;best_disp=disp
                        if l>=maxl:break
            if best_len>=3:
                flag|=(1<<(7-bit))
                b0=((best_len-3)<<4)|((best_disp-1)>>8)
                b1=(best_disp-1)&0xff
                tokens.append(b0);tokens.append(b1)
                pos+=best_len
            else:
                tokens.append(data[pos]);pos+=1
        out.append(flag);out+=tokens
    return bytes(out)

def decode(src,size):
    out=bytearray();sp=4
    while len(out)<size and sp<len(src):
        fl=src[sp];sp+=1
        for b in range(7,-1,-1):
            if len(out)>=size:break
            if fl&(1<<b):
                b0,b1=src[sp],src[sp+1];sp+=2
                L=(b0>>4)+3;D=(((b0&0xf)<<8)|b1)+1
                si=0x10000+len(out)-D
                for k in range(L):
                    if len(out)>=size:break
                    j=si+k
                    out.append(0 if j<0x10000 else out[j-0x10000])
            else:
                out.append(src[sp]);sp+=1
    return bytes(out)

if __name__=='__main__':
    import os,random
    random.seed(1)
    # test with zero window semantics: data should reference zeros at start
    t=bytes([0,0,0,0,1,2,3,1,2,3,1,2,3])+bytes(random.randrange(256) for _ in range(200))
    e=encode2(t)
    d=decode(e,len(t))
    print('roundtrip',d==t,'ratio',len(e)/len(t))
