import struct, zlib, os

BASE='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
OUT='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms'
GP=0x20b6000

def crc16(data):
    crc=0xFFFF
    for b in data:
        crc^=b
        for _ in range(8):
            if crc&1: crc=(crc>>1)^0xA001
            else: crc>>=1
    return crc&0xFFFF

orig=open(BASE,'rb').read()
print('=== NDS HEADER ===')
for name,path in [('orig',BASE),('vA',OUT+'/Sonic3D_vA_keepdesc.nds'),('vB',OUT+'/Sonic3D_vB_size4m.nds')]:
    d=open(path,'rb').read()
    print(name,'size',hex(len(d)),
          'romsz@80',hex(struct.unpack_from('<I',d,0x80)[0]),
          'hdrcrc@15c',hex(struct.unpack_from('<H',d,0x15c)[0]),
          'calc_crc(0..15d)',hex(crc16(d[:0x15e])),
          'logocrc@15e',hex(struct.unpack_from('<H',d,0x15e)[0]))
    # header first 0x200 identical?
    print('   header[0:0x200]==orig?', d[:0x200]==orig[:0x200])

print()
print('=== FAT entries ===')
for name,path in [('orig',BASE),('vA',OUT+'/Sonic3D_vA_keepdesc.nds')]:
    d=open(path,'rb').read()
    fntoff,fntsz,fatoff,fatsz=struct.unpack_from('<IIII',d,0x40)
    fat=d[fatoff:fatoff+fatsz]
    print(name,'fatoff',hex(fatoff),'fatsz',hex(fatsz))
    for i in (0,7,8):
        s,e=struct.unpack_from('<II',fat,i*8)
        print(f'  file{i}: {hex(s)}..{hex(e)} sz={hex(e-s)}')

print()
print('=== byte diff summary per region (vA vs orig) ===')
va=open(OUT+'/Sonic3D_vA_keepdesc.nds','rb').read()
regions=[('header',0,0x200),('pak_hdr',GP,GP+0x51000),('pak_data',GP+0x51000,GP+len(orig)-GP),
         ('other_files',0x200,GP)]
for nm,s,e in regions:
    e=min(e,len(orig))
    n=sum(1 for a,b in zip(orig[s:e],va[s:e]) if a!=b)
    print(f'  {nm:12s} [{hex(s)}..{hex(e)}] diffbytes={n}/{e-s}')

print()
print('=== descriptor region diff (pak+0x400..0x900) ===')
for i in range(GP+0x400,GP+0x900,16):
    if orig[i:i+16]!=va[i:i+16]:
        print(f'  {hex(i-GP)}: orig={orig[i:i+16].hex()}  vA={va[i:i+16].hex()}')
