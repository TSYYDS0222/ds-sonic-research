import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "melonds-mcp", "mcp", "python"))
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask
ROM="D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds"
emu=EmulatorState(); print("open",emu.open_rom(ROM),flush=True)
def tap(x,y,w=45):
    emu.lib.lib.melonds_input_set_touch_pos(x,y);emu.advance_frames(10)
    emu.lib.lib.melonds_input_release_touch();emu.advance_frames(w)
def key(k,w=30,h=6):
    emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask([k]));emu.advance_frames(h)
    emu.lib.lib.melonds_input_keypad_update(0);emu.advance_frames(w)
def wait(n):emu.advance_frames(n)
wait(60);tap(128,140,90);wait(60);key('a',60);wait(60)
# 在解压函数下断点
bid=emu.lib.lib.melonds_debug_bp_add(0,0x020844B8)
print("bp id",bid,flush=True)
tap(128,49,60);wait(30);tap(225,185,40)
r=emu.run_until_break(max_frames=120)
print("break result",r,flush=True)
regs=emu.lib.get_registers(0)
print("regs r0-r12:",[hex(x) for x in regs[:13]],flush=True)
# 读 r0 指向的源数据头
src=regs[0]
hdr=emu.lib.peek_block(0,src,32)
print("src",hex(src),"hdr:",hdr.hex(),flush=True)
dst=regs[1]
print("dst",hex(dst),flush=True)
