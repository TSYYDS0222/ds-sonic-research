import struct, os, shutil

NDS='D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'
MD='D:/tsyyds/shijiamoniqi2.11/Sonic 3D Blast (USA, Europe, Korea) (En).md'
OUT='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms/Sonic3D_injected.nds'
GP=0x20b6000; GPSZ=5355024
DATA_START=GP+0x51000          # pak 数据区起点 (绝对 ROM 地址)
PAGE=0x10000
NPAGE=64

def swab(b):
    return bytes(x for pr in zip(b[1::2],b[0::2]) for x in pr)

# 读 ROM
rom=open(MD,'rb').read()
assert len(rom)<=NPAGE*PAGE
rom=rom.ljust(NPAGE*PAGE,b'\xff')   # pad
print('MD rom',len(rom))

# swab -> pak 裸页数据
pakdata=swab(rom)
assert len(pakdata)==NPAGE*PAGE

# 64 页写入 NDS ROM 数据区 (覆盖原 pak 数据区前 4MB)
nds=bytearray(open(NDS,'rb').read())
assert len(nds)==0x4000000, hex(len(nds))
for i in range(NPAGE):
    off=DATA_START+i*PAGE
    nds[off:off+PAGE]=pakdata[i*PAGE:(i+1)*PAGE]
print('wrote 64 raw pages to',hex(DATA_START),'..',hex(DATA_START+NPAGE*PAGE))

# 重建两组页表: @GP+0x8 和 @GP+0x5c0, 各 128 项 {addr,size}
# 表项 i -> 68K 页 i; 页 0..63 = ROM 0..4MB, 页 64..127 = 镜像(同 ROM)
for tbl_off in (0x8,0x5c0):
    for i in range(128):
        page_idx=i & 63
        addr=DATA_START+page_idx*PAGE
        struct.pack_into('<II',nds,GP+tbl_off+8*i,addr,PAGE)
    print('rebuilt page table @pak+0x%x'%tbl_off)

# 改 6 个 descriptor 的 size 字段 -> 4MB, base -> 数据起点
# descriptor 起点: 0x410,0x454,0x49c,0x4e4,0x52c,0x574 (size 在 +0xc/+0x10)
# 保守起见只改 4 个真实游戏的 size 为 0x400000, 保持 base 不变(页表已重定向)
# 实际模拟器按 descriptor.size 决定拷贝页数 -> 必须改
DESCS=[(0x410,0xc),(0x454,0x10),(0x49c,0x10),(0x4e4,0x10),(0x52c,0x10),(0x574,0x10)]
for dbase,soff in DESCS:
    old=struct.unpack_from('<I',nds,GP+dbase+soff)[0]
    struct.pack_into('<I',nds,GP+dbase+soff,0x400000)
    print(f'desc@0x{dbase:x} size {hex(old)} -> 0x400000')

# 游戏名改为 SONIC 3D BLAST (pak+0x900 起 4 个名字槽)
names=[0x900,0x918,0x930,0x944]
label=b'SONIC 3D BLAST'.ljust(0x18,b'\0')
for no in names:
    nds[GP+no:GP+no+0x18]=label[:0x18]

os.makedirs(os.path.dirname(OUT),exist_ok=True)
open(OUT,'wb').write(nds)
print('WROTE',OUT,os.path.getsize(OUT))
