import struct, itertools

ROM = 'D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
GP, GPSZ = 0x020b6000, 5355024
fh = open(ROM, 'rb'); fh.seek(GP); pak = fh.read(GPSZ)
recs = [struct.unpack_from('<II', pak, 8 + 8 * i) for i in range(128)]

def blob(i):
    o, s = recs[i]
    return pak[o-GP:o-GP+s]

def decode(d, len_add, disp_add, order, ring=65536, carry=None):
    size = d[1] | d[2] << 8 | d[3] << 16
    if size == 0 or size > 0x40000: return None
    p = 4
    out = bytearray(ring)
    if carry is not None:
        out[:len(carry)] = carry[-ring:]
    nw = 0
    bits = range(7, -1, -1) if order == 'msb' else range(8)
    guard = 0
    while nw < size:
        if p >= len(d): return None
        fl = d[p]; p += 1
        for i in bits:
            if nw >= size: break
            if fl & (1 << i):
                if p + 1 >= len(d): return None
                b0 = d[p]; b1 = d[p+1]; p += 2
                L = (b0 >> 4) + len_add
                D = (((b0 & 0xF) << 8) | b1) + disp_add
                src = nw - D
                if src < -ring: return None
                for k in range(L):
                    if nw >= size: break
                    out[nw % ring] = out[(src + k) % ring]; nw += 1
            else:
                if p >= len(d): return None
                out[nw % ring] = d[p]; nw += 1; p += 1
    return bytes(out[:min(size, ring)])

# 只解前 8 个真实压缩块做快速判据
targets = [i for i in range(128) if blob(i)[:1] == b'\x11' and recs[i][1] > 0x1000][:4]
print('test banks', targets)
best = []
for len_add, disp_add, order in itertools.product([1, 2, 3], [0, 1], ['msb', 'lsb']):
    ok = 0; tot = 0; sega = 0
    for i in targets:
        r = decode(blob(i), len_add, disp_add, order)
        tot += 1
        if r is not None:
            ok += 1
            if b'SEGA' in r: sega += 1
    best.append((sega, ok, tot, len_add, disp_add, order))
for b in sorted(best, reverse=True)[:8]:
    print('sega=%d ok=%d/%d len+%d disp+%d %s' % b)
