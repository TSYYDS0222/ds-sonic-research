import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "melonds-mcp", "mcp", "python"))
from PIL import Image
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask
ROM="../SCC_extract/roms/MK_v18_real.nds"
emu=EmulatorState(); print("open",emu.open_rom(os.path.abspath(ROM)),flush=True)
def shot(n):
    raw=emu.lib.screenshot_bytes();t=raw[:256*192*3];b=raw[256*192*3:]
    im=Image.new("RGB",(256,384));im.putdata([tuple(t[i:i+3]) for i in range(0,len(t),3)]+[tuple(b[i:i+3]) for i in range(0,len(b),3)])
    im.save(f"v18_{n}.png");print("shot",n,flush=True)
def tap(x,y,w=50):
    emu.lib.lib.melonds_input_set_touch_pos(x,y);emu.advance_frames(10)
    emu.lib.lib.melonds_input_release_touch();emu.advance_frames(w)
def key(k,w=25,h=6):
    emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask([k]));emu.advance_frames(h)
    emu.lib.lib.melonds_input_keypad_update(0);emu.advance_frames(w)
def wait(n):emu.advance_frames(n)
wait(60);tap(128,140,90);wait(60);key('a',60);wait(60)
tap(128,49,60);wait(30)
shot('00_list')
# 选第3个游戏: 右键2次
key('right',20);wait(15);key('right',20);wait(15)
shot('01_slot3')
tap(225,185,60)
for i,f in enumerate([180,300,400,500]):
    wait(f);shot(f't{i+1}')
print('status',emu.lib.get_status(),flush=True)
