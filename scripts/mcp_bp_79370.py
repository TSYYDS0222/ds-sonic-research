import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'melonds-mcp', 'mcp', 'python'))
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask
ROM = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.abspath('../SCC_extract/roms/MK_probe_blockD.nds')
emu = EmulatorState(); emu.open_rom(ROM)
def stats():
    raw = emu.lib.screenshot_bytes()[:256*192*3]
    return sum(raw)/len(raw), len(set(tuple(raw[i:i+3]) for i in range(0,len(raw),3)))
def waitmenu():
    for _ in range(120):
        m,c=stats()
        if m>100 and c>1000: return
        emu.advance_frames(10)
def tap(x,y,hold=10,wait=60):
    emu.lib.lib.melonds_input_set_touch_pos(x,y); emu.advance_frames(hold)
    emu.lib.lib.melonds_input_release_touch(); emu.advance_frames(wait)
emu.advance_frames(60); tap(128,140,10,90)
emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask(['a'])); emu.advance_frames(5)
emu.lib.lib.melonds_input_keypad_update(0); emu.advance_frames(60); waitmenu()
tap(128,49,8,50); emu.advance_frames(20)
emu.lib.lib.melonds_debug_bp_add(0,0x02079370)
tap(225,185,8,30)
for i in range(6):
    r=emu.advance_frames(120)
    if not r['break_hit']: break
    regs=emu.lib.get_registers(0)
    stack=emu.lib.peek_block(0,regs[13],0x20)
    ws=[int.from_bytes(stack[j:j+4],'little') for j in range(0,len(stack),4)]
    print(i,'r0-r12',' '.join(f'{x:08x}' for x in regs[:13]),flush=True)
    print('   tail',' '.join(f'{x:08x}' for x in regs[13:]),flush=True)
    if i == 0:
        try:
            st = emu.lib.peek_block(0, 0x02085840, 0x40)
            ws = [int.from_bytes(st[j:j + 4], 'little') for j in range(0, len(st), 4)]
            print('   STATE',' '.join(f'{w:08x}' for w in ws), flush=True)
            dp = ws[2]
            de = emu.lib.peek_block(0, dp, 0x20)
            dw = [int.from_bytes(de[j:j + 4], 'little') for j in range(0, len(de), 4)]
            print('   DESC', hex(dp), ' '.join(f'{w:08x}' for w in dw), flush=True)
            tb = emu.lib.peek_block(0, 0x025E5000, 0x40)
            print('   TBLRAM', tb.hex(), flush=True)
            for ra in (0x023D1CC0, 0x023D19D0, 0x023D1020):
                rb = emu.lib.peek_block(0, ra, 0x40)
                rw = [int.from_bytes(rb[j:j + 4], 'little') for j in range(0, len(rb), 4)]
                print(f'   RAMT {ra:08x}: ' + ' '.join(f'{w:08x}' for w in rw), flush=True)
        except Exception as e:
            print('   STATE ERR', e, flush=True)
    print('   stack',' '.join(f'{w:08x}' for w in ws),flush=True)
    emu.continue_after_break()
