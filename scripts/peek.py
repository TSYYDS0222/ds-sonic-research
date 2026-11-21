import sys
D='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/rom_pages'

def sw(b):
    out=bytearray(len(b))
    out[0::2]=b[1::2]
    out[1::2]=b[0::2]
    return bytes(out)

b=sw(open(D+'/page_032.bin','rb').read())
lines=[]
for i in range(0,0x140,16):
    hx=' '.join('%02x'%x for x in b[i:i+16])
    asc=''.join(chr(x) if 32<=x<127 else '.' for x in b[i:i+16])
    lines.append('%04x: %-47s %s'%(i,hx,asc))
print('\n'.join(lines))
sys.stdout.flush()
