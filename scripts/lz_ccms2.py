"""扩展 token 版 LZ77 编码器（与 0x020844B8 解压器完全对应）。

原 lz_ccms.encode 只用了短 token (L<=16)，所以 MK 页压缩到 ~0xBA77，
塞不进合集原始 0x87xx 的压缩块槽。这里补上解压器本来就支持的
3 字节/4 字节长匹配 token，把压缩率提上去。
"""
WINSIZE = 0x10000
MAXDIST = 0x1000
MAXMATCH = 0x1000

def _encode_token(L, D):
    if L < 3 or D < 1 or D > MAXDIST:
        return None
    if L <= 16:
        b0 = ((L - 1) << 4) | (((D - 1) >> 8) & 0xF)
        if b0 & 0xE0 == 0:
            return None
        return bytes([b0, (D - 1) & 0xFF])
    if L <= 256:
        base = L - 0x11
        b0 = base >> 4
        nib = base & 0xF
        r5v = (nib << 4) | (((D - 1) >> 8) & 0xF)
        return bytes([b0, r5v, (D - 1) & 0xFF])
    base = L - 0x111
    if base < 0 or (base >> 12) > 0xF:
        return None
    b0 = 0x10 | ((base >> 12) & 0xF)
    b1 = (base >> 4) & 0xFF
    nib = base & 0xF
    r5v = (nib << 4) | (((D - 1) >> 8) & 0xF)
    return bytes([b0, b1, r5v, (D - 1) & 0xFF])

def _token_len(tok):
    return {2: 2, 3: 3, 4: 4}[len(tok)]

def encode(data, tries=48):
    n = len(data)
    out = bytearray([0x11, n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF])
    head = {}
    prev = {}
    pos = 0
    while pos < n:
        flag = 0
        tokens = bytearray()
        for bit in range(8):
            if pos >= n:
                break
            best_L = 0
            best_D = 0
            if pos + 3 <= n:
                key = (data[pos] << 16) | (data[pos + 1] << 8) | data[pos + 2]
                cand = head.get(key)
                vpos = WINSIZE + pos
                maxL = min(MAXMATCH, n - pos)
                count = 0
                while cand is not None and count < tries:
                    D = vpos - cand
                    if D < 1 or D > MAXDIST:
                        break
                    cpos = cand - WINSIZE
                    L = 0
                    while L < maxL and data[cpos + L] == data[pos + L]:
                        L += 1
                    if L > best_L:
                        best_L = L; best_D = D
                        if L >= maxL:
                            break
                    cand = prev.get(cand); count += 1
                if vpos <= MAXDIST:
                    L = 0
                    while L < maxL and data[pos + L] == 0:
                        L += 1
                    if L > best_L:
                        best_L = L; best_D = vpos
            tok = _encode_token(best_L, best_D) if best_L >= 3 else None
            if tok is not None:
                flag |= 1 << (7 - bit)
                tokens += tok
                end = pos + best_L
                for k in range(pos, end):
                    if k + 3 <= n:
                        kk = (data[k] << 16) | (data[k + 1] << 8) | data[k + 2]
                        vk = WINSIZE + k
                        prev[vk] = head.get(kk); head[kk] = vk
                pos = end
            else:
                tokens.append(data[pos])
                if pos + 3 <= n:
                    key = (data[pos] << 16) | (data[pos + 1] << 8) | data[pos + 2]
                    vk = WINSIZE + pos
                    prev[vk] = head.get(key); head[key] = vk
                pos += 1
        out.append(flag); out += tokens
    return bytes(out)

def decode(src, size):
    hdr = int.from_bytes(src[:4], 'little')
    mode = hdr & 0xF
    p = 4; out = bytearray()
    lr = 0; bc = 0
    while len(out) < size and p < len(src):
        if bc == 0:
            lr = src[p]; p += 1; bc = 8
        bit = (lr >> 7) & 1
        lr = (lr << 1) & 0xFF; bc -= 1
        if bit == 0:
            out.append(src[p]); p += 1
        else:
            b0 = src[p]
            if mode == 0:
                r6 = 3; r5v = b0
            elif (b0 & 0xE0) != 0:
                r6 = 1; r5v = b0
            else:
                p += 1
                r6 = (b0 & 0xF) << 4
                if b0 & 0x10:
                    r6 <<= 8
                    b1 = src[p]; p += 1
                    r6 += b1 << 4
                    r6 += 0x100
                r6 += 0x11
                r5v = src[p]
            L = r6 + (r5v >> 4)
            p += 1
            b1 = src[p]; p += 1
            D = (b1 | ((r5v & 0xF) << 8)) + 1
            for _ in range(L):
                idx = len(out) - D
                out.append(out[idx] if idx >= 0 else 0)
    return bytes(out)

if __name__ == '__main__':
    import time
    mk = open('D:/Users/江口小学/mortal-kombat.md','rb').read()
    def swab(b): return bytes(x for p in zip(b[1::2], b[0::2]) for x in p)
    page = swab(mk[:0x10000])
    t = time.time(); c = encode(page); dt = time.time() - t
    print('len', hex(len(c)), 'time', round(dt, 2), 'roundtrip', decode(c, len(page)) == page)
