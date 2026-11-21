import struct
d=open('../SCC_extract/files/Game.pak','rb').read()
# descriptor 疑似起点: 0x410,0x450,0x490,0x4d0 但字段错位. 
# 从 name ptr (0x023d79xx) 出现位置反推真实结构起点
# 名字串在 pak+0x900(Sonic2),0x918(Sonic3),0x930(Sonic1),0x944(S&K)
# RAM base = 0x023d7000 => name ptr - 0x023d7000 = pak offset
name_off={0x900:'Sonic2',0x918:'Sonic3',0x930:'Sonic1',0x944:'S&K'}
# 找所有指向名字串的 u32
print('=== name ptr refs ===')
for i in range(0x408,0x900,4):
    v=struct.unpack_from('<I',d,i)[0]
    if 0x23d7000<=v<0x23d8000:
        off=v-0x23d7000
        print(f'pak+0x{i:x} -> pak+0x{off:x} ({name_off.get(off,"?")})')

#  descriptor 里有 0x80000/0x100000/0x200000/0x300000 = size
#  和 0x020f7000/0x02197000/0x02267000/... = base ROM addr
print('\n=== size/base candidates ===')
for i in range(0x408,0x600,4):
    v=struct.unpack_from('<I',d,i)[0]
    if v in (0x80000,0x100000,0x200000,0x300000,0x400000) or (0x20b6000<=v<0x25d1610 and v&0xffff==0x7000):
        print(f'pak+0x{i:x} = 0x{v:x}')
