import struct, zlib, hashlib

ROM='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
d=open(ROM,'rb').read()
def swab(b): return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

# blob0: CRC stored=0x133c86ee, data=blob[0x10:0x80000], swab valid 68K code
base,sz,stored=0x20f7000,0x80000,0x133c86ee
data=d[base+0x10:base+sz]
sw=swab(data)

found=[]
def chk(label,v):
    if (v&0xffffffff)==stored: found.append(label)

# crc32 with all byte orders / offsets
for bufname,buf in (('raw',data),('swab',sw)):
    chk(f'crc32({bufname})',zlib.crc32(buf))
    chk(f'~crc32({bufname})',~zlib.crc32(buf))
    for off in (0,0x100,0x200):
        chk(f'crc32({bufname}[{off}:])',zlib.crc32(buf[off:]))
    # byteswapped 32bit words view
    w32=b''.join(struct.pack('>I',x) for x in struct.unpack('<%dI'%(len(buf)//4),buf[:len(buf)//4*4]))
    chk(f'crc32(sw32({bufname}))',zlib.crc32(w32))
    # reversed
    chk(f'crc32(rev({bufname}))',zlib.crc32(buf[::-1]))

# md5/sha first4
for bufname,buf in (('raw',data),('swab',sw)):
    chk(f'md5({bufname})[:4]',struct.unpack('<I',hashlib.md5(buf).digest()[:4])[0])
    chk(f'sha1({bufname})[:4]',struct.unpack('<I',hashlib.sha1(buf).digest()[:4])[0])

# sum/checksum variants over sw
for label,v in [
    ('sum32(sw)',sum(struct.unpack('<%dI'%(len(sw)//4),sw[:len(sw)//4*4]))),
    ('sum16(sw)',sum(struct.unpack('<%dH'%(len(sw)//2),sw[:len(sw)//2*2]))),
    ('sum8(sw)',sum(sw)),
    ('nsum16(sw)',~sum(struct.unpack('<%dH'%(len(sw)//2),sw[:len(sw)//2*2]))),
]:
    chk(label,v)

print('MATCHES:',found if found else 'NONE of common algorithms')
print('stored:',hex(stored))
# print what each first-region crc gives, maybe CRC is only over header fields
hdr=d[base:base+0x10]
print('crc32(data) =',hex(zlib.crc32(data)&0xffffffff))
print('crc32(sw)   =',hex(zlib.crc32(sw)&0xffffffff))
print('hint: perhaps CRC field is not verified, or is content ID')
