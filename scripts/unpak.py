import struct

ROM = 'D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
GP, GPSZ = 0x020b6000, 5355024
fh = open(ROM, 'rb'); fh.seek(GP); pak = fh.read(GPSZ)
recs = [struct.unpack_from('<II', pak, 8 + 8 * i) for i in range(128)]

def lz11(d):
    size = d[1] | d[2] << 8 | d[3] << 16
    p = 4; out = bytearray()
    while len(out) < size:
        if p >= len(d): return None
        flags = d[p]; p += 1
        for i in range(7, -1, -1):
            if len(out) >= size: break
            if flags & (1 << i):
                if p + 1 >= len(d): return None
                b0 = d[p]; b1 = d[p+1]; p += 2
                n = (b0 >> 4) + 3
                disp = (((b0 & 0xF) << 8) | b1) + 1
                s = len(out) - disp
                if s < 0: return None
                for k in range(n):
                    if len(out) >= size: break
                    out.append(out[s+k])
            else:
                if p >= len(d): return None
                out.append(d[p]); p += 1
    return bytes(out)

banks = []
for i, (o, s) in enumerate(recs):
    blob = pak[o-GP:o-GP+s]
    if blob[:1] in (b'\x11', b'\x10'):
        d = lz11(blob)
        if d is None:
            print(i, 'FAIL'); d = b''
    else:
        d = blob
    banks.append(d)
    if i < 5 or i > 122:
        print(f'bank {i:3d} raw={s:6d} out={len(d):6d} head={d[:8].hex()}')

img = b''.join(banks)
print('image size', len(img), hex(len(img)))
open('md_image.bin', 'wb').write(img)

# 找 Genesis 头
import re
for m in re.finditer(b'SEGA', img):
    o = m.start()
    seg = img[o:o+32]
    if b'MEGA' in seg or b'GENESIS' in seg:
        print('GENESIS HDR at', hex(o), seg)
print('--- strings ---')
for kw in [b'MEGA DRIVE', b'GENESIS', b'SONIC', b'SEGA']:
    hits = [hex(m.start()) for m in re.finditer(re.escape(kw), img)][:10]
    print(kw, hits)
