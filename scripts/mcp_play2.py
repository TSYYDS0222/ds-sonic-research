import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "melonds-mcp", "mcp", "python"))
from PIL import Image
from melonds_mcp.emulator import EmulatorState
ROM = sys.argv[1] if len(sys.argv)>1 else "../SCC_extract/roms/MK_v1_clean.nds"
L = sys.argv[2] if len(sys.argv)>2 else "p2"
W,H=256,192
emu=EmulatorState(); print("open",emu.open_rom(os.path.abspath(ROM)))
def shot(n):
    raw=emu.lib.screenshot_bytes(); t=raw[:W*H*3]; b=raw[W*H*3:W*H*6]
    img=Image.new("RGB",(W,H*2)); img.putdata([tuple(t[i:i+3]) for i in range(0,len(t),3)]+[tuple(b[i:i+3]) for i in range(0,len(b),3)])
    img.save(f"{L}_{n}.png"); print("shot",n)
def tap(x,y,w=50):
    emu.lib.lib.melonds_input_set_touch_pos(x,y); emu.advance_frames(5)
    emu.lib.lib.melonds_input_release_touch(); emu.advance_frames(w)
def press(k,w=40):
    from melonds_mcp.constants import buttons_to_bitmask
    emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask([k])); emu.advance_frames(5)
    emu.lib.lib.melonds_input_keypad_update(0); emu.advance_frames(w)
emu.advance_frames(60)
tap(128,140)   # 中文
emu.advance_frames(180)  # 过版权
shot("01_menu")
tap(128,140)   # JUEGOS
shot("02_games")
