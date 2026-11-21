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
emu.lib.lib.melonds_debug_bp_add(0,0x020844B8)
tap(128,49,60);wait(30);key('right',20);wait(15);key('right',20);wait(15)
tap(225,185,40)
# 第一次断点: 记录 src/dst
r=emu.advance_frames(120)
regs=emu.lib.get_registers(0)
src,dst=regs[0],regs[1]
print('entry src=%08x dst=%08x'%(src,dst),flush=True)
# dump 源 LZ 块头
print('lz src head',emu.lib.peek_block(0,src,16).hex(),flush=True)
# ack, 单步到函数返回(用 step 大量指令), 然后读 dst
emu.continue_after_break()
emu.lib.lib.melonds_debug_bp_clear(0)
wait(30)   # 让解压完成
b=emu.lib.peek_block(0,dst,0x20)
print('after decompress dst:',b.hex(),flush=True)
def swab(x):return bytes(v for p in zip(x[1::2],x[0::2]) for v in p)
print('swab:',swab(b).hex(),flush=True)
