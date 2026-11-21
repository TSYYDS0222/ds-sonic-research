import struct, itertools

ROM = 'D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
GP, GPSZ = 0x020b6000, 5355024
fh = open(ROM, 'rb'); fh.seek(GP); pak = fh.read(GPSZ)
recs = [struct.unpack_from('<II', pak, 8 + 8 * i) for i in range(128)]
blobs = [pak[o-GP:o-GP+s] for o, s in recs]

def dec(d, flip, ordm, la, da, swap, hdr):
    size = d[1] | d[2] << 8 | d[3] << 16
    if not (0x4000 <= size <= 0x10000): return None
    p = hdr; out = bytearray()
    bits = range(7, -1, -1) if ordm else range(8)
    while len(out) < size:
        if p >= len(d): return None
        fl = d[p]; p += 1
        for i in bits:
            if len(out) >= size: break
            isref = bool(fl & (1 << i)) ^ flip
            if isref:
                if p + 1 >= len(d): return None
                b0, b1 = d[p], d[p+1]; p += 2
                if swap: b0, b1 = b1, b0
                L = (b0 >> 4) + la
                D = (((b0 & 0xF) << 8) | b1) + da
                s = len(out) - D
                if s < 0: return None
                for k in range(L):
                    if len(out) >= size: break
                    if s + k >= len(out): return None
                    out.append(out[s + k])
            else:
                if p >= len(d): return None
                out.append(d[p]); p += 1
    return bytes(out)

best = []
for flip, ordm, la, da, swap, hdr in itertools.product([0, 1], [0, 1], [1, 2, 3, 4], [0, 1], [0, 1], [4]):
    ok = 0; hit = 0
    for b in blobs:
        if b[:1] != b'\x11': continue
        r = dec(b, flip, ordm, la, da, swap, hdr)
        if r is None: continue
        ok += 1
        if b'SEGA' in r[:0x200]: hit += 1
    if ok: best.append((hit, ok, flip, ordm, la, da, swap, hdr))
best.sort(reverse=True)
print('hit ok flip ord la da swap hdr')
for x in best[:8]: print(x)
