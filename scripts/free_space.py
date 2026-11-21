import struct
ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d=open(ROM,'rb').read()
fatsz=struct.unpack_from('<I',d,0x4c)[0]
fatoff=struct.unpack_from('<I',d,0x48)[0]
fat=d[fatoff:fatoff+fatsz]
print('=== files ===')
mx=0
for i in range(fatsz//8):
    s,e=struct.unpack_from('<II',fat,i*8)
    print(f'  file{i}: 0x{s:08x}..0x{e:08x} size=0x{e-s:x}')
    mx=max(mx,e)
print('max file end',hex(mx),'ROM size',hex(len(d)))
print('free tail',hex(len(d)-mx),'=',len(d)-mx,'bytes')

# check tail content
print('tail sample @',hex(mx),':',d[mx:mx+32].hex())
print('rom last 32:',d[-32:].hex())

# find if region after max is all 0xFF
tail=d[mx:]
print('tail all FF?',all(x==0xff for x in tail),'distinct',len(set(tail)))
