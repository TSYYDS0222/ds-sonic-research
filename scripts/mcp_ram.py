import sys, os, struct
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "melonds-mcp", "mcp", "python"))
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask
ROM=sys.argv[1]; W,H=256,192
emu=EmulatorState(); print("open",emu.open_rom(os.path.abspath(ROM)),flush=True)
def tap(x,y,w=60):
    emu.lib.lib.melonds_input_set_touch_pos(x,y);emu.advance_frames(10)
    emu.lib.lib.melonds_input_release_touch();emu.advance_frames(w)
def key(k,w=25,h=6):
    emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask([k]));emu.advance_frames(h)
    emu.lib.lib.melonds_input_keypad_update(0);emu.advance_frames(w)
def wait(n):emu.advance_frames(n)
wait(60);tap(128,140,90);wait(60);key("a",60);wait(60)
tap(128,49,90);wait(30);tap(225,185,60);wait(1200)  # 进游戏
print("status",emu.lib.get_status(),flush=True)
# dump ARM9 main RAM 0x02000000..0x02400000 (4MB) in 4KB chunks
base=0x02000000; total=0x400000
data=bytearray()
for off in range(0,total,0x1000):
    data+=emu.lib.peek_block(0,base+off,0x1000)
print("dumped",len(data),flush=True)
open("arm9_ram_at_game.bin","wb").write(data)
# 搜索 0x00FF0000 (68K SP in D0/A7 area)
pat=struct.pack('<I',0x00FF0000)
hits=[m for m in range(len(data)) if data[m:m+4]==pat]
print("0xFF0000 hits",len(hits),[hex(base+h) for h in hits[:30]],flush=True)
# 搜索注入数据特征: MK ROM swab 头 'ESAG' at DATA-relative
# 我们的数据写在 file 0x3420000, 但映射地址? 搜 'SEGA'/'ESAG' in RAM
for kw in [b'SEGA',b'ESAG',b'MORTAL',b'LATNOM']:
    h=[m for m in range(len(data)) if data[m:m+len(kw)]==kw]
    print(kw,len(h),[hex(base+x) for x in h[:10]],flush=True)
