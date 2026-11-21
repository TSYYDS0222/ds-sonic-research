import re, struct
D='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/rom_pages'
def sw(b):
    o=bytearray(len(b)); o[0::2]=b[1::2]; o[1::2]=b[0::2]; return bytes(o)

print('=== 每页起始 SP/PC (swab后) ===')
for i in range(128):
    b=sw(open(f'{D}/page_{i:03d}.bin','rb').read())
    sp,pc=struct.unpack_from('>II',b,0)
    if sp in (0x00ff0000,0x00fffffe,0x00ff8000,0x00ffffff) or (0x00000000<pc<0x00010000 and sp>=0x00f00000):
        print('page%3d SP=%08x PC=%08x @100=%s'%(i,sp,pc,b[0x100:0x110].hex()))
print()
print('=== 标题串所在页 ===')
for i in range(128):
    b=sw(open(f'{D}/page_{i:03d}.bin','rb').read())
    for kw in (b'SEGA MEGA DRIVE',b'SEGA GENESIS',b'(C)SEGA',b'SONIC THE HEDGEHOG'):
        m=re.search(re.escape(kw),b[:0x400])
        if m: print(f'page{i:3d} +{m.start():04x} {kw.decode()} | {b[m.start():m.start()+60]}')
