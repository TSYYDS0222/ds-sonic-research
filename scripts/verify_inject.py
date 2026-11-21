import struct, re
OUT='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms/Sonic3D_injected.nds'
GP=0x20b6000
nds=open(OUT,'rb').read()

def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

print('=== injected page tables ===')
for tbl in (8,0x5c0):
    e0=struct.unpack_from('<II',nds,GP+tbl)
    print(f'tbl@0x{tbl:x} first entry addr={e0[0]:08x} size={e0[1]:08x}')
    assert e0[1]==0x10000

print('\n=== reconstruct ROM from table (first 64 pages) ===')
img=bytearray()
for i in range(64):
    a,s=struct.unpack_from('<II',nds,GP+8+8*i)
    assert s==0x10000, (i,hex(s))
    img+=nds[a:a+s]
img=bytes(img)
sw=swab(img)
print('len',len(sw))
print('head',sw[:0x20].hex())
print('at 0x100:',sw[0x100:0x140])
for kw in (b'SEGA GENESIS',b'SONIC 3D',b'(C)SEGA',b'GENESIS'):
    print(kw,[hex(m.start()) for m in re.finditer(re.escape(kw),sw)][:5])

# compare to source
src=open('D:/tsyyds/shijiamoniqi2.11/Sonic 3D Blast (USA, Europe, Korea) (En).md','rb').read().ljust(0x400000,b'\xff')
print('\nmatch source:',sw[:len(src)]==src)
