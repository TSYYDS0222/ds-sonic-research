import sys,os
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
# 在解压函数返回后 0x02084594 下断点 (pop {r4-r7,lr}; bx lr)
emu.lib.lib.melonds_debug_bp_add(0,0x02084594)
tap(128,49,60);wait(30);key('right',20);wait(15);key('right',20);wait(15)
tap(225,185,40)
r=emu.advance_frames(120)
print('break',r.get('break_hit'),flush=True)
regs=emu.lib.get_registers(0)
print('r0(src)=%08x r1(dst)=%08x'%(regs[0],regs[1]),flush=True)
# 此时 dst 刚被写入, dump 目标页
dst=regs[1]
b=emu.lib.peek_block(0,dst,0x20)
print('at decompress dst head:',b.hex(),flush=True)
def swab(x):return bytes(v for p in zip(x[1::2],x[0::2]) for v in p)
print('swab:',swab(b).hex(),flush=True)
