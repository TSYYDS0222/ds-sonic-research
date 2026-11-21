"""合集游戏ROM解压器专用 LZ77 编码器.
解压器 @0x020844B8 token 语义:
  头 u32: (len<<8)|0x11, 解压长度 = hdr>>8, mode = hdr&0xF
  flags 字节 MSB-first
  bit=0: literal
  bit=1: b0=*src; r6 = 1 (when b0&0xE0); L = r6 + (b0>>4) = 1+(b0>>4)
         b1=*++src; D = ((b0&0xF)<<8 | b1) + 1
         从 dst-D 拷贝 L 字节
"""
WINSIZE = 0x10000
MINLEN = 3      # b0MINLEN = 2      # L 最小可以是 1, 但 <2 不划算0xE0 must be nonzero -> (L-1)>=2 -> L>=3
MAXLEN = 16     # L = 1 + (b0>>4), b0>>4 <= 0xF -> L <= 16

def encode(data, mode=1):
    n = len(data)
    out = bytearray([0x11, n & 0xff, (n>>8)&0xff, (n>>16)&0xff])
    # 注意 mode 放进头低字节: 头 = (n<<8) | 0x11 -> 低字节 0x11, mode=1
    head = {}
    prev = {}
    pos = 0
    while pos < n:
        flag = 0
        tokens = bytearray()
        for bit in range(8):
            if pos >= n: break
            best_len = 0; best_disp = 0
            if pos + 3 <= n:
                key = (data[pos]<<16)|(data[pos+1]<<8)|data[pos+2]
                cand = head.get(key)
                vpos = WINSIZE + pos
                tries = 0
                while cand is not None and tries < 48:
                    disp = vpos - cand
                    if disp < 1 or disp > 0xfff: break
                    l = 0
                    while l < MAXLEN and pos+l < n:
                        a = 0 if cand+l < WINSIZE else data[cand+l-WINSIZE]
                        if a == data[pos+l]: l += 1
                        else: break
                    if l > best_len:
                        best_len = l; best_disp = disp
                        if l >= MAXLEN: break
                    cand = prev.get(cand); tries += 1
                if vpos <= 0xfff:
                    l = 0
                    while l < MAXLEN and pos+l < n and data[pos+l] == 0: l += 1
                    if l > best_len:
                        best_len = l; best_disp = vpos
            if best_len >= MINLEN:
                flag |= (1 << (7-bit))
                # L = 1 + (b0>>4)  => b0>>4 = L-1
                b0 = (((best_len-1)&0xF)<<4) | (((best_disp-1)>>8)&0xf)
                b1 = (best_disp-1)&0xff
                tokens.append(b0); tokens.append(b1)
                for k in range(pos, pos+best_len):
                    if k+3 <= n:
                        kk=(data[k]<<16)|(data[k+1]<<8)|data[k+2]
                        vk=WINSIZE+k
                        prev[vk]=head.get(kk); head[kk]=vk
                pos += best_len
            else:
                tokens.append(data[pos])
                if pos+3 <= n:
                    key=(data[pos]<<16)|(data[pos+1]<<8)|data[pos+2]
                    vk=WINSIZE+pos
                    prev[vk]=head.get(key); head[key]=vk
                pos += 1
        out.append(flag); out += tokens
    return bytes(out)

def decode(src, size):
    """严格按解压器汇编 0x020844B8 翻译 (mode 由头低字节决定)."""
    hdr = int.from_bytes(src[:4],'little')
    mode = hdr & 0xf
    p = 4; out = bytearray()
    lr = 0; bc = 0
    while len(out) < size and p < len(src):
        if bc == 0:
            lr = src[p]; p += 1; bc = 8
        bit = (lr>>7)&1
        lr = (lr<<1)&0xff; bc -= 1
        if bit == 0:
            # ldrb r6,[r0],#1; swpb -> 输出字节即字面量
            out.append(src[p]); p += 1
        else:
            b0 = src[p]
            if mode == 0:
                r6 = 3
                r5v = b0
            elif (b0 & 0xe0) != 0:
                r6 = 1
                r5v = b0
            else:
                # 扩展 token: add r0,#1 (跳过 b0)
                p += 1
                r6 = (b0 & 0xf) << 4
                if b0 & 0x10:
                    r6 <<= 8
                    b1 = src[p]; p += 1
                    r6 += b1 << 4
                    r6 += 0x100
                r6 += 0x11
                r5v = src[p]        # ldrb r5,[r0]  (common 里 add r0,#1 消费它)
            r3 = r6 + (r5v >> 4)    # 长度
            p += 1                  # add r0,#1 (消费 r5v 所在字节)
            r5low = r5v & 0xf
            b1 = src[p]; p += 1     # ldrb r6,[r0],#1
            D = (b1 | (r5low<<8)) + 1
            for _ in range(r3):
                idx = len(out) - D
                out.append(out[idx] if idx >= 0 else 0)
    return bytes(out)

if __name__ == '__main__':
    import time
    mk = open('D:/Users/江口小学/mortal-kombat.md','rb').read()
    def swab(b): return bytes(x for p in zip(b[1::2],b[0::2]) for x in p)
    for lbl, page in [('raw', mk[:0x10000]), ('swab', swab(mk[:0x10000]))]:
        t=time.time(); c=encode(page); dt=time.time()-t
        r=decode(c, len(page))
        print(lbl, 'ratio', round(len(c)/len(page),3), 'time', round(dt,2), 'roundtrip', r==page)
