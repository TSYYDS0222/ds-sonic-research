import sys, struct
sys.path.insert(0, 'C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/work')
from lz_ccms import decode

P = 'D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d = open(P, 'rb').read()
t = 0x20B6000 + 0x5C0

def sw(b):
    return bytes(x for q in zip(b[1::2], b[0::2]) for x in q)

for i in range(104):
    a, s = struct.unpack_from('<II', d, t + 8 * i)
    if not (0 < a < len(d) and 1 <= s < 0x20000):
        print(f'{i:3d} {a:08x} {s:6x} BAD')
        continue
    try:
        u = decode(d[a:a + s], 0x10000)
        r = sw(u)
    except Exception as e:
        print(f'{i:3d} {a:08x} {s:6x} ERR {e}')
        continue
    print(f'{i:3d} {a:08x} {s:6x} {r[:8].hex()} {r[0x100:0x110]!r}')
