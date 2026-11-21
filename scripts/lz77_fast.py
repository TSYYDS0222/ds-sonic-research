"""Fast DS LZ77 type 0x11 encoder - hash table based, 64KB zero preset window."""
import struct

WINSIZE=0x10000
MAXLEN=18
MINLEN=3

def encode(data):
    n=len(data)
    out=bytearray([0x11,n&0xff,(n>>8)&0xff,(n>>16)&0xff])
    # hash: 3-byte key -> list of virtual positions (most recent first)
    # virtual stream = WINSIZE zeros + data; position v = WINSIZE + i
    head={}          # key -> most recent vpos
    prev={}          # vpos -> previous vpos with same key (only within data + zeros)
    pos=0
    # seed: zeros already in window; we can match against zeros via special handling
    while pos<n:
        flag=0;tokens=bytearray()
        for bit in range(8):
            if pos>=n: break
            best_len=0;best_disp=0
            if pos+MINLEN<=n:
                key=(data[pos]<<16)|(data[pos+1]<<8)|data[pos+2]
                cand=head.get(key)
                vpos=WINSIZE+pos
                tries=0
                while cand is not None and tries<32:
                    disp=vpos-cand
                    if disp<1 or disp>0xfff: break
                    # length
                    l=0
                    while l<MAXLEN and pos+l<n:
                        # byte at virtual pos cand+l
                        if cand+l<WINSIZE:
                            a=0
                        else:
                            a=data[cand+l-WINSIZE]
                        if a==data[pos+l]: l+=1
                        else: break
                    if l>best_len:
                        best_len=l;best_disp=disp
                        if l>=MAXLEN: break
                    cand=prev.get(cand);tries+=1
                # also try zero-run match: disp = vpos (source=0)
                if vpos<=0xfff:
                    l=0
                    while l<MAXLEN and pos+l<n and data[pos+l]==0: l+=1
                    if l>best_len:
                        best_len=l;best_disp=vpos
            if best_len>=MINLEN:
                flag|=(1<<(7-bit))
                b0=((best_len-MINLEN)<<4)|((best_disp-1)>>8)
                b1=(best_disp-1)&0xff
                tokens.append(b0);tokens.append(b1)
                # insert all positions covered by match into hash
                for k in range(pos,pos+best_len):
                    if k+MINLEN<=n:
                        kk=(data[k]<<16)|(data[k+1]<<8)|data[k+2]
                        vk=WINSIZE+k
                        prev[vk]=head.get(kk)
                        head[kk]=vk
                pos+=best_len
            else:
                tokens.append(data[pos])
                if pos+MINLEN<=n:
                    key=(data[pos]<<16)|(data[pos+1]<<8)|data[pos+2]
                    vk=WINSIZE+pos
                    prev[vk]=head.get(key)
                    head[key]=vk
                pos+=1
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
                si=WINSIZE+len(out)-D
                for k in range(L):
                    if len(out)>=size:break
                    j=si+k
                    out.append(0 if j<WINSIZE else out[j-WINSIZE])
            else:
                out.append(src[sp]);sp+=1
    return bytes(out)

if __name__=='__main__':
    import time
    d=open('D:/tsyyds/shijiamoniqi2.11/Sonic 3D Blast (USA, Europe, Korea) (En).md','rb').read()
    def swab(b):return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)
    p=swab(d[:0x10000])
    t=time.time();c=encode(p);dt=time.time()-t
    ok=decode(c,len(p))==p
    print('one page',dt,'ratio',len(c)/len(p),'roundtrip',ok)
