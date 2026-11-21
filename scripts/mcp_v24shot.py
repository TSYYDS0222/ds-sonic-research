import sys,os
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"melonds-mcp","mcp","python"))
from PIL import Image
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask
emu=EmulatorState();emu.open_rom(os.path.abspath('../SCC_extract/roms/MK_v24_allslots.nds'))
def shot(n):
    r=emu.lib.screenshot_bytes();t=r[:256*192*3];b=r[256*192*3:]
    im=Image.new("RGB",(256,384));im.putdata([tuple(t[i:i+3]) for i in range(0,len(t),3)]+[tuple(b[i:i+3]) for i in range(0,len(b),3)])
    im.save(f"v24_{n}.png");print("shot",n,flush=True)
def tap(x,y,w=40):
    emu.lib.lib.melonds_input_set_touch_pos(x,y);emu.advance_frames(8)
    emu.lib.lib.melonds_input_release_touch();emu.advance_frames(w)
def key(k,w=20,h=5):
    emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask([k]));emu.advance_frames(h)
    emu.lib.lib.melonds_input_keypad_update(0);emu.advance_frames(w)
def wait(n):emu.advance_frames(n)
wait(50);tap(128,140,70);wait(50);key('a',50);wait(50)
tap(128,49,50);wait(20);shot('00_list');tap(225,185,30);wait(200);shot('01_intro')
for i in range(4):key('start',15);key('a',15);wait(20)
wait(300);shot('02_game')
