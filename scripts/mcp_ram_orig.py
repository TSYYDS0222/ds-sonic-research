import sys, os, struct
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "melonds-mcp", "mcp", "python"))
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask
ROM="D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds"
emu=EmulatorState(); print("open",emu.open_rom(ROM),flush=True)
def tap(x,y,w=60):
    emu.lib.lib.melonds_input_set_touch_pos(x,y);emu.advance_frames(10)
    emu.lib.lib.melonds_input_release_touch();emu.advance_frames(w)
def key(k,w=25,h=6):
    emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask([k]));emu.advance_frames(h)
    emu.lib.lib.melonds_input_keypad_update(0);emu.advance_frames(w)
def wait(n):emu.advance_frames(n)
wait(60);tap(128,140,90);wait(60);key("a",60);wait(60)
tap(128,49,90);wait(30);tap(225,185,60);wait(1200)
print("status",emu.lib.get_status(),flush=True)
base=0x02000000; data=bytearray()
for off in range(0,0x400000,0x1000): data+=emu.lib.peek_block(0,base+off,0x1000)
open("arm9_ram_orig_game.bin","wb").write(data)
for kw in [b'SEGA',b'ESAG',b'SONIC',b'CNOIS']:
    h=[m for m in range(len(data)) if data[m:m+len(kw)]==kw]
    print(kw,len(h),[hex(base+x) for x in h[:8]],flush=True)
