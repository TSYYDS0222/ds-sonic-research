import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "melonds-mcp", "mcp", "python"))
from PIL import Image
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask
ROM=sys.argv[1]; L=sys.argv[2]; W,H=256,192
emu=EmulatorState(); print("open",emu.open_rom(os.path.abspath(ROM)),flush=True)
def shot(n):
    raw=emu.lib.screenshot_bytes();t=raw[:W*H*3];b=raw[W*H*3:W*H*6]
    im=Image.new("RGB",(W,H*2));im.putdata([tuple(t[i:i+3]) for i in range(0,len(t),3)]+[tuple(b[i:i+3]) for i in range(0,len(b),3)])
    im.save(f"{L}_{n}.png");print("shot",n,flush=True)
def tap(x,y,w=60):
    emu.lib.lib.melonds_input_set_touch_pos(x,y);emu.advance_frames(10)
    emu.lib.lib.melonds_input_release_touch();emu.advance_frames(w)
def key(k,w=20,h=6):
    emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask([k]));emu.advance_frames(h)
    emu.lib.lib.melonds_input_keypad_update(0);emu.advance_frames(w)
def wait(n):emu.advance_frames(n)
wait(60);tap(128,140,90);wait(60);key("a",60);wait(60)
tap(128,49,90);wait(30)
shot("00_list")
# 用右键切换游戏槽, 每个槽启动看画面, 然后返回
for slot in range(4):
    if slot>0: key("right",25);wait(20)
    shot(f"s{slot}_selected")
    tap(225,185,60);wait(180)   # INICIAR
    shot(f"s{slot}_game")
    # 返回: 触控左上角 ATRAS 约 x=15,y=180
    tap(15,180,60);key("b",30);wait(60)
print("done",flush=True)
