import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "melonds-mcp", "mcp", "python"))
from PIL import Image
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask
ROM=sys.argv[1]; L="s2"; W,H=256,192
emu=EmulatorState(); print("open",emu.open_rom(os.path.abspath(ROM)))
def shot(n):
    raw=emu.lib.screenshot_bytes();t=raw[:W*H*3];b=raw[W*H*3:W*H*6]
    im=Image.new("RGB",(W,H*2));im.putdata([tuple(t[i:i+3]) for i in range(0,len(t),3)]+[tuple(b[i:i+3]) for i in range(0,len(b),3)])
    im.save(f"{L}_{n}.png");print("shot",n)
def tap(x,y,w=50):
    emu.lib.lib.melonds_input_set_touch_pos(x,y);emu.advance_frames(10)
    emu.lib.lib.melonds_input_release_touch();emu.advance_frames(w)
def key(k,w=45,h=6):
    emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask([k]));emu.advance_frames(h)
    emu.lib.lib.melonds_input_keypad_update(0);emu.advance_frames(w)
def wait(n):emu.advance_frames(n)
wait(60);tap(128,140,90);wait(60);key("a",60);wait(60)
shot("00_menu")
# 这次不点JUEGOS, 先看主菜单. 用触控点 JUEGOS 后立即狂按A(跳过可能的开场)
emu.lib.lib.melonds_input_set_touch_pos(128,137);wait(10);emu.lib.lib.melonds_input_release_touch();wait(30)
shot("01_click")
# 连续按住 START 长时间 (跳过动画)
emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask(["start"]));wait(120)
emu.lib.lib.melonds_input_keypad_update(0);wait(30)
shot("02_starthold")
for i in range(5):
    emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask(["a"]));wait(60)
    emu.lib.lib.melonds_input_keypad_update(0);wait(60)
    shot(f"03_a{i}")
