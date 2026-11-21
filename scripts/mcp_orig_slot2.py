import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "melonds-mcp", "mcp", "python"))
from PIL import Image
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask
emu=EmulatorState();emu.open_rom(os.path.abspath('../SCC_extract/roms/D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds'))
def shot(n):
    raw=emu.lib.screenshot_bytes();t=raw[:256*192*3];b=raw[256*192*3:]
    im=Image.new("RGB",(256,384));im.putdata([tuple(t[i:i+3]) for i in range(0,len(t),3)]+[tuple(b[i:i+3]) for i in range(0,len(b),3)])
    im.save(f"v18b_{n}.png");print("shot",n,flush=True)
def tap(x,y,w=50):
    emu.lib.lib.melonds_input_set_touch_pos(x,y);emu.advance_frames(10)
    emu.lib.lib.melonds_input_release_touch();emu.advance_frames(w)
def key(k,w=25,h=6):
    emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask([k]));emu.advance_frames(h)
    emu.lib.lib.melonds_input_keypad_update(0);emu.advance_frames(w)
def wait(n):emu.advance_frames(n)
wait(60);tap(128,140,90);wait(60);key('a',60);wait(60)
tap(128,49,60);wait(30);key('right',20);wait(15);key('right',20);wait(15)
tap(225,185,60);wait(300)
# 介绍页 -> 按 START/A 进入游戏
for i in range(5):
    key('start',30);key('a',30);wait(60)
shot('00_after_start')
for i,f in enumerate([300,600,900]):
    wait(f);shot(f't{i+1}')
    print('pc',hex(emu.lib.get_status()[6]),flush=True)
