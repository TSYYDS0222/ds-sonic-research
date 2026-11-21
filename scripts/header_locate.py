import re
ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d=open(ROM,'rb').read()
def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

# Search entire S2 CCMS blob for SEGA header (raw and swab)
b2=d[0x2197000:0x2197000+0x100000]
b2sw=swab(b2)
print('=== SEGA/title in S2 blob RAW ===')
for kw in (b'SEGA',b'GENESIS',b'SONIC THE',b'(C)'):
    print(f'  {kw}: {[hex(m.start()) for m in re.finditer(re.escape(kw),b2)][:8]}')
print('=== SEGA/title in S2 blob SWAB ===')
for kw in (b'SEGA',b'GENESIS',b'SONIC THE',b'(C)'):
    print(f'  {kw}: {[hex(m.start()) for m in re.finditer(re.escape(kw),b2sw)][:8]}')

# SP/PC: Sonic2 header SP=00FF0000 PC=00000206 -> swab in blob = 0000FF00 ...?
# standard header at ROM 0x0: 00FF0000 00000206 ; swab16 -> FF000000 06020000
print('\n=== search SP/PC signatures ===')
for pat,name in [(bytes.fromhex('00ff0000 00000206'),'normal'),
                 (bytes.fromhex('ff000000 06020000'),'swab16'),
                 (bytes.fromhex('0000ff00 06020000'),'swap32')]:
    print(f'  {name}: raw={[hex(m.start()) for m in re.finditer(re.escape(pat),b2)][:5]} swab={[hex(m.start()) for m in re.finditer(re.escape(pat),b2sw)][:5]}')

# dump blob header + first 0x120 swabbed
print('\n=== S2 blob swab first 0x120 ===')
s=b2sw
for i in range(0,0x120,16):
    print(f'  {i:04x}: {s[i:i+16].hex()}  {s[i:i+16]}')
