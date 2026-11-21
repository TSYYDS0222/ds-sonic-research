import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "melonds-mcp", "mcp", "python"))
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask
ROM="D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds"
emu=EmulatorState();emu.open_rom(ROM)
def tap(x,y,w=45):
    emu.lib.lib.melonds_input_set_touch_pos(x,y);emu.advance_frames(10)
    emu.lib.lib.melonds_input_release_touch();emu.advance_frames(w)
def key(k,w=30,h=6):
    emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask([k]));emu.advance_frames(h)
    emu.lib.lib.melonds_input_keypad_update(0);emu.advance_frames(w)
def wait(n):emu.advance_frames(n)
wait(60);tap(128,140,90);wait(60);key('a',60);wait(60)
bid=emu.lib.lib.melonds_debug_bp_add(0,0x020844B8)
tap(128,49,60);wait(30);tap(225,185,40)
emu.run_until_break(max_frames=120)
regs=emu.lib.get_registers(0)
src=regs[0]
# dump 0x2160000 LZ77 前 0x30000
data=bytearray()
for off in range(0,0x30000,0x1000): data+=emu.lib.peek_block(0,src+off,0x1000)
open('lz_src_at_2160000.bin','wb').write(data)
print('lz header',data[:32].hex(),flush=True)
import struct
sz=data[1]|data[2]<<8|data[3]<<16
print('lz declared size',hex(sz),flush=True)
# 对比 CCMS blob
nds=open(ROM,'rb').read()
blob=nds[0x20f7000:0x20f7000+0x30000]
print('ccms blob head',blob[:32].hex(),flush=True)
print('lz==ccms?',bytes(data[:0x100])==blob[:0x100],flush=True)
