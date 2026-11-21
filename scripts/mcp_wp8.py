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
# 在 8 个页目标下写监视点: 0x2170000 + i*0x10000
for pg in range(8):
    emu.lib.lib.melonds_debug_wp_add(0,0x2170000+pg*0x10000,4,2)
# 也在 LZ 源 RAM 区 0x2160000 下读监视, 抓源块
emu.lib.lib.melonds_debug_wp_add(0,0x2160000,4,1)
tap(128,49,60);wait(30);tap(225,185,40)
all_ev=[]
for _ in range(20):
    wait(30)
    all_ev+=emu.lib.wp_events()
print("total events",len(all_ev),flush=True)
targets=sorted(set(e['address'] for e in all_ev))
pcs=sorted(set(e['pc'] for e in all_ev))
print("targets:",[hex(x) for x in targets],flush=True)
print("pcs:",[hex(x) for x in pcs],flush=True)
