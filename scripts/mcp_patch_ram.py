import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "melonds-mcp", "mcp", "python"))
from PIL import Image
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask
ROM=sys.argv[1]; W,H=256,192
TARGET=0x2170000
emu=EmulatorState(); print("open",emu.open_rom(os.path.abspath(ROM)),flush=True)
def shot(n):
    raw=emu.lib.screenshot_bytes();t=raw[:W*H*3];b=raw[W*H*3:W*H*6]
    im=Image.new("RGB",(W,H*2));im.putdata([tuple(t[i:i+3]) for i in range(0,len(t),3)]+[tuple(b[i:i+3]) for i in range(0,len(b),3)])
    im.save(f"patch_{n}.png");print("shot",n,flush=True)
def tap(x,y,w=60):
    emu.lib.lib.melonds_input_set_touch_pos(x,y);emu.advance_frames(10)
    emu.lib.lib.melonds_input_release_touch();emu.advance_frames(w)
def key(k,w=25,h=6):
    emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask([k]));emu.advance_frames(h)
    emu.lib.lib.melonds_input_keypad_update(0);emu.advance_frames(w)
def wait(n):emu.advance_frames(n)
wait(60);tap(128,140,90);wait(60);key("a",60);wait(60)
tap(128,49,90);wait(30);tap(225,185,60);wait(900)
shot("00_sonic_before")
# MK ROM swab
mk=open("D:/Users/江口小学/mortal-kombat.md","rb").read().ljust(0x200000,b'\xff')
sw=bytes(x for pr in zip(mk[1::2],mk[0::2]) for x in pr)
print("writing",len(sw),"bytes to",hex(TARGET),flush=True)
for off in range(0,len(sw),0x1000):
    emu.lib.poke_block(0,TARGET+off,sw[off:off+0x1000])
print("write done",flush=True)
wait(120);shot("01_after_patch")
wait(300);shot("02_after_more")
