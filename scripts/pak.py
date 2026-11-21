import struct, sys, os

ROM = 'D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
GP, GPSZ = 0x020b6000, 5355024
f = open(ROM, 'rb')

def lz77(d, p=0):
    t = d[p]
    if t == 0x10:
        size = d[p+1] | d[p+2] << 8 | d[p+3] << 16
    else:
        size = d[p+1] | d[p+2] << 8 | d[p+3] << 16
    p += 4
    out = bytearray()
    while len(out) < size:
        if p >= len(d): return None
        flags = d[p]; p += 1
        for i in range(7, -1, -1):
            if len(out) >= size: break
            if flags & (1 << i):
                b0 = d[p]; b1 = d[p+1]; p += 2
                n = (b0 >> 4) + 3
                disp = (((b0 & 0xF) << 8) | b1) + 1
                s = len(out) - disp
                if s < 0: return None
                for k in range(n):
                    out.append(out[s+k])
            else:
                out.append(d[p]); p += 1
    return bytes(out), p

f.seek(GP); pak = f.read(GPSZ)
hdr = struct.unpack_from('<II', pak, 0)
print('header', [hex(x) for x in hdr])
recs = []
off = 8
while off + 8 <= 0x900:
    o, s = struct.unpack_from('<II', pak, off)
    recs.append((o, s)); off += 8
print('records', len(recs))

# 验证
ok = 0; bad = []
for i, (o, s) in enumerate(recs):
    if not (GP <= o <= GP + GPSZ - 1): bad.append((i, o, s, 'range'))
    elif o + s > GP + GPSZ: bad.append((i, o, s, 'overrun'))
    else: ok += 1
print('valid', ok, 'bad', len(bad), bad[:5])
print('sum sizes', sum(s for o, s in recs), 'pak', GPSZ)

# 解压
types = {}
chunks = []
for i, (o, s) in enumerate(recs):
    blob = pak[o-GP:o-GP+s]
    t = blob[0]
    types[t] = types.get(t, 0) + 1
    if t in (0x10, 0x11):
        r = lz77(blob)
        if r: chunks.append((i, o, s, t, r[0]))
        else: chunks.append((i, o, s, t, blob))
    else:
        chunks.append((i, o, s, t, blob))
print('first-byte histogram', types)
print('decompressed sizes sample', [(c[0], len(c[4])) for c in chunks[:8]])
total = sum(len(c[4]) for c in chunks)
print('total decompressed', total)
open('chunks.bin', 'wb').write(b''.join(c[4] for c in chunks))
