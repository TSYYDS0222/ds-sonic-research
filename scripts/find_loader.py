import struct, re

d=open('rom.bin','rb').read()
a9=d[0x4000:0x4000+537728]
base=0x2004000

# search for CCMS magic references and descriptor-area pointers in ARM9
print('=== CCMS magic 0x534D4343 refs ===')
pat=struct.pack('<I',0x534d4343)
for m in re.finditer(re.escape(pat),a9):
    print('  ref @',hex(base+m.start()))

print('=== descriptor RAM ptr refs (0x023d7000..0x023d8000) ===')
cnt=0
for o in range(0,len(a9)-4,4):
    w=struct.unpack_from('<I',a9,o)[0]
    if 0x023d7000<=w<0x023d8000:
        print(f'  @{base+o:08x} -> {w:08x}')
        cnt+=1
        if cnt>40: break

print('=== game ROM base refs (0x020f7000 etc) ===')
for t in (0x20f7000,0x2197000,0x2267000,0x2347000,0x2367000,0x2377000,0x2107000):
    pat=struct.pack('<I',t)
    hits=[base+m.start() for m in re.finditer(re.escape(pat),a9)]
    print(f'  {t:08x}: {[hex(h) for h in hits[:8]]}')

print('=== "CCMS" bytes in whole ROM ===')
for m in re.finditer(b'CCMS',d):
    print('  ',hex(m.start()))
