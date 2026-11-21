import sys,os,capstone
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"melonds-mcp","mcp","python"))
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask
emu=EmulatorState();emu.open_rom(os.path.abspath('../SCC_extract/roms/MK_v22_final.nds'))
def tap(x,y,w=45):
    emu.lib.lib.melonds_input_set_touch_pos(x,y);emu.advance_frames(10)
    emu.lib.lib.melonds_input_release_touch();emu.advance_frames(w)
def key(k,w=25,h=6):
    emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask([k]));emu.advance_frames(h)
    emu.lib.lib.melonds_input_keypad_update(0);emu.advance_frames(w)
def wait(n):emu.advance_frames(n)
wait(60);tap(128,140,90);wait(60);key('a',60);wait(60)
tap(128,49,60);wait(30);key('right',20);wait(15);key('right',20);wait(15)
tap(225,185,40);wait(400)
regs=emu.lib.get_registers(0)
print('regs r0-r15:',[hex(x) for x in regs[:16]],flush=True)
print('status',emu.lib.get_status(),flush=True)
# 追踪最后200条指令, 范围 0xFFFF0000..0xFFFF0200 看谁跳进来(可能trace到)
emu.lib.lib.melonds_debug_trace_start(1,0,0xffffffff)
wait(30)
emu.lib.lib.melonds_debug_trace_stop()
ents=emu.lib.trace_drain(200)
print('trace count',len(ents),flush=True)
for e in ents[:10]+ents[-10:]:
    print('  ',{k:hex(v) for k,v in e.items()},flush=True)
