import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "melonds-mcp", "mcp", "python"))
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask
emu=EmulatorState();emu.open_rom(os.path.abspath('../SCC_extract/roms/MK_v19_5c0only.nds'))
def tap(x,y,w=45):
    emu.lib.lib.melonds_input_set_touch_pos(x,y);emu.advance_frames(10)
    emu.lib.lib.melonds_input_release_touch();emu.advance_frames(w)
def key(k,w=25,h=6):
    emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask([k]));emu.advance_frames(h)
    emu.lib.lib.melonds_input_keypad_update(0);emu.advance_frames(w)
def wait(n):emu.advance_frames(n)
wait(60);tap(128,140,90);wait(60);key('a',60);wait(60)
tap(128,49,60);wait(30);key('right',20);wait(15);key('right',20);wait(15)
tap(225,185,60);wait(600)
# dump 0x2100000..0x2240000
data=bytearray()
for off in range(0x2100000,0x2240000,0x1000):
    try:data+=emu.lib.peek_block(0,off,0x1000)
    except:data+=b'\x00'*0x1000
open('v19_ram.bin','wb').write(data)
# 搜 MK 头两种形式
for pat,nm in [(bytes.fromhex('ffff020000000200'),'MK_BE'),(bytes.fromhex('ffff000200000002'),'MK_swab')]:
    hits=[0x2100000+i for i in range(len(data)) if data[i:i+8]==pat]
    print(nm,[hex(h) for h in hits[:10]],'count',len(hits),flush=True)
# 搜 SONIC3 头
for pat,nm in [(b'SEGA',b'SEGA'.decode()),(b'ESAG','ESAG')]:
    hits=[0x2100000+i for i in range(len(data)) if data[i:i+4]==pat]
    print(nm,[hex(h) for h in hits[:10]],flush=True)
