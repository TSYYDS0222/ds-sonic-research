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
emu.lib.lib.melonds_debug_bp_add(0,0x020844B8)
tap(128,49,60);wait(30);tap(225,185,40)
srcs=[]
for it in range(40):
    r=emu.advance_frames(120)
    if not r['break_hit']:
        break
    regs=emu.lib.get_registers(0)
    r0=regs[0]; r1=regs[1]; r4=regs[4]
    # 读压缩头拿解压大小
    try:
        hdr=emu.lib.peek_block(0,r0,4)
        dsz=hdr[1]|hdr[2]<<8|hdr[3]<<16
    except: dsz=0
    srcs.append((r0,r1,r4,hex(dsz)))
    emu.continue_after_break()
print("hits",len(srcs),flush=True)
for s in srcs[:40]: print("  srcRAM=%08x dst=%08x fileSrc=%08x dsz=%s"%s,flush=True)
