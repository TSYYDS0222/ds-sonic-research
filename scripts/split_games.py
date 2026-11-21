import re, os, struct
D='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/rom_pages'
OUT='C:/Users/江口小学/WorkBuddy/2026-11-15-16-06-53/SCC_extract/roms'
os.makedirs(OUT,exist_ok=True)

# 真实 ROM = 前64页 (后64页是镜像)
img=b''.join(open(f'{D}/page_{i:03d}.swab.bin','rb').read() for i in range(64))
open(OUT+'/combined_4mb.swab.bin','wb').write(img)
print('combined 4MB written')
for kw in (b'(C)SEGA',b'SONIC',b'KNUCKLES',b'1991',b'1992',b'1994'):
    hits=[(hex(m.start()),img[max(0,m.start()-16):m.start()+50]) for m in re.finditer(re.escape(kw),img)]
    print(kw.decode(),len(hits))
    for h in hits[:8]: print('  ',h[0],h[1])

# 每16页=1MB 一个游戏
names=['game_0_0MB','game_1_1MB','game_2_2MB','game_3_3MB']
for g in range(4):
    part=img[g*0x100000:(g+1)*0x100000]
    p=OUT+f'/{names[g]}.md'
    open(p,'wb').write(part)
    tags=[m.group() for m in re.finditer(rb'\(C\)SEGA[ -~]{0,40}',part)][:3]
    print(names[g],'size',len(part),'tags',tags)
