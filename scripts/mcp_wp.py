import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "melonds-mcp", "mcp", "python"))
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask
ROM="D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds"
emu=EmulatorState(); print("open",emu.open_rom(ROM),flush=True)
def tap(x,y,w=50):
    emu.lib.lib.melonds_input_set_touch_pos(x,y);emu.advance_frames(10)
    emu.lib.lib.melonds_input_release_touch();emu.advance_frames(w)
def key(k,w=35,h=6):
    emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask([k]));emu.advance_frames(h)
    emu.lib.lib.melonds_input_keypad_update(0);emu.advance_frames(w)
def wait(n):emu.advance_frames(n)
# 导航到主菜单 (监视点还没下, 避免菜单阶段干扰)
wait(60);tap(128,140,90);wait(60);key("a",60);wait(60)
# 下写监视点: 0x2170000 起 0x100 字节
wp=emu.lib.lib.melonds_debug_wp_add(0,0x2170000,0x100,2)  # 2=write
print("wp id",wp,flush=True)
# 点 JUEGOS 再 INICIAR 触发加载
tap(128,49,60);wait(30)
tap(225,185,60)
ev=emu.lib.wp_events()
print("events after start",len(ev),flush=True)
for e in ev[:15]: print("  ",{k:hex(v) for k,v in e.items()},flush=True)
wait(300)
ev=emu.lib.wp_events()
print("events after 300",len(ev),flush=True)
for e in ev[:15]: print("  ",{k:hex(v) for k,v in e.items()},flush=True)
