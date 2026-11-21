import struct, itertools

ROM = 'D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
GP, GPSZ = 0x020b6000, 5355024
fh = open(ROM, 'rb'); fh.seek(GP); pak = fh.read(GPSZ)
recs = [struct.unpack_from('<II', pak, 8 + 8 * i) for i in range(128)]
blobs = []
for i, (o, s) in enumerate(recs):
    b = pak[o-GP:o-GP+s]
    if b[:1] == b'\x11' and s > 0x2000:
        blobs.append(b)
print('compressed blobs', len(blobs))
sample = blobs[:12]

def run(d, len_add, disp_add, order, swap, hdr=4):
    size = d[1] | d[2] << 8 | d[3] << 16
    if size != 0x10000: return None
    p = hdr
    out = bytearray(); 
    bits = range(7, -1, -1) if order == 'msb' else range(8)
    while len(out) < size:
        if p >= len(d): return None
        fl = d[p]; p += 1
        for i in bits:
            if len(out) >= size: break
            if fl & (1 << i):
                if p + 1 >= len(d): return None
                b0 = d[p]; b1 = d[p+1]; p += 2
                if not swap:
                    L = (b0 >> 4) + len_add; D = (((b0 & 0xF) << 8) | b1) + disp_add
                else:
                    L = (b1 >> 4) + len_add; D = (((b1 & 0xF) << 8) | b0) + disp_add
                s = len(out) - D
                if s < 0: return None
                for k in range(L):
                    if len(out) >= size: break
                    if s + k >= len(out): return None
                    out.append(out[s+k])
            else:
                if p >= len(d): return None
                out.append(d[p]); p += 1
    return len(out), p

res = []
for la, da, order, swap, hdr in itertools.product([1, 2, 3, 4], [0, 1, 2], ['msb', 'lsb'], [0, 1], [4, 5]):
    good = 0; waste = 0; n = 0
    for d in sample:
        r = run(d, la, da, order, swap, hdr)
        n += 1
        if r:
            good += 1; waste += len(d) - r[1]
    res.append((good, -waste, la, da, order, swap, hdr))
res.sort(reverse=True)
for r in res[:10]:
    print('good=%d/%d waste=%d len+%d disp+%d %s swap=%d hdr=%d' % (r[0], len(sample), -r[1], r[2], r[3], r[4], r[5], r[6]))
