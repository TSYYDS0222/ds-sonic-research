import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "melonds-mcp", "mcp", "python"))
from PIL import Image
from melonds_mcp.emulator import EmulatorState
ROM=sys.argv[1]; L="tp"; W,H=256,192
emu=EmulatorState(); print("open",emu.open_rom(os.path.abspath(ROM)))
def shot(n):
    raw=emu.lib.screenshot_bytes();t=raw[:W*H*3];b=raw[W*H*3:W*H*6]
    im=Image.new("RGB",(W,H*2));im.putdata([tuple(t[i:i+3]) for i in range(0,len(t),3)]+[tuple(b[i:i+3]) for i in range(0,len(b),3)])
    im.save(f"{L}_{n}.png");print("shot",n)
def tap(x,y,w=50):
    emu.lib.lib.melonds_input_set_touch_pos(x,y);emu.advance_frames(10)
    emu.lib.lib.melonds_input_release_touch();emu.advance_frames(w)
emu.advance_frames(60);tap(128,140,90);emu.advance_frames(150)
shot("00_menu")
# 试不同y值点JUEGOS, 每次重置不可能, 只能顺序试并观察
# JUEGOS 在主菜单下屏 y约137(从图看). 用较长按压
emu.lib.lib.melonds_input_set_touch_pos(128,137);emu.advance_frames(15)
shot("01_touch_held")   # 按住时截图, 看是否高亮
emu.lib.lib.melonds_input_release_touch();emu.advance_frames(90)
shot("02_released")
