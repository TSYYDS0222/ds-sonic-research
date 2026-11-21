import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "melonds-mcp", "mcp", "python"))
from PIL import Image
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask
ROM=sys.argv[1]; L=sys.argv[2]; W,H=256,192
emu=EmulatorState(); print("open",emu.open_rom(os.path.abspath(ROM)))
def shot(n):
    raw=emu.lib.screenshot_bytes();t=raw[:W*H*3];b=raw[W*H*3:W*H*6]
    im=Image.new("RGB",(W,H*2));im.putdata([tuple(t[i:i+3]) for i in range(0,len(t),3)]+[tuple(b[i:i+3]) for i in range(0,len(b),3)])
    im.save(f"{L}_{n}.png");print("shot",n)
def tap(x,y,w=45):
    emu.lib.lib.melonds_input_set_touch_pos(x,y);emu.advance_frames(6)
    emu.lib.lib.melonds_input_release_touch();emu.advance_frames(w)
def key(k,w=40,h=6):
    emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask([k]));emu.advance_frames(h)
    emu.lib.lib.melonds_input_keypad_update(0);emu.advance_frames(w)
def wait(n):emu.advance_frames(n)
wait(60)
tap(128,140,90);wait(150)  # 语言 -> 版权
# 版权画面按 A 跳过
key("a",80);shot("01_after_a")
# 主菜单应该出现. 用方向键选第一个(JUEGOS)再A
key("up",20);key("a",80);shot("02_gamelist_try")
