import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'melonds-mcp', 'mcp', 'python'))
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask

ROM = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.abspath('../SCC_extract/roms/MK_probe_blockD.nds')
emu = EmulatorState(); emu.open_rom(ROM)

def stats():
    raw = emu.lib.screenshot_bytes()[:256 * 192 * 3]
    return sum(raw) / len(raw), len(set(tuple(raw[i:i + 3]) for i in range(0, len(raw), 3)))

def waitmenu():
    for _ in range(120):
        m, c = stats()
        if m > 100 and c > 1000:
            return
        emu.advance_frames(10)

def tap(x, y, hold=10, wait=60):
    emu.lib.lib.melonds_input_set_touch_pos(x, y); emu.advance_frames(hold)
    emu.lib.lib.melonds_input_release_touch(); emu.advance_frames(wait)

emu.advance_frames(60)
tap(128, 140, 10, 90)
emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask(['a'])); emu.advance_frames(5)
emu.lib.lib.melonds_input_keypad_update(0); emu.advance_frames(60)
waitmenu()
tap(128, 49, 8, 50)
emu.advance_frames(20)
emu.lib.lib.melonds_debug_bp_add(0, 0x020844B8)
tap(225, 185, 8, 30)

hits = []
for it in range(60):
    r = emu.advance_frames(120)
    if not r['break_hit']:
        break
    regs = emu.lib.get_registers(0)
    src, dst, size = regs[0], regs[1], regs[3]
    try:
        srchead = emu.lib.peek_block(0, src, 16).hex()
    except Exception as e:
        srchead = 'ERR:' + str(e)
    allregs = emu.lib.get_registers(0)
    if not hits:
        try:
            stack = emu.lib.peek_block(0, allregs[13], 0x80)
            words = [int.from_bytes(stack[i:i + 4], 'little') for i in range(0, len(stack), 4)]
            print('STACK', ' '.join(f'{w:08x}' for w in words), flush=True)
        except Exception as e:
            print('STACK ERR', e, flush=True)
        try:
            import struct
            pat = struct.pack('<I', src if False else 0x01A76B73)
            found = []
            for addr in range(0x02000000, 0x02200000, 0x1000):
                blk = emu.lib.peek_block(0, addr, 0x1000)
                off = 0
                while True:
                    off = blk.find(pat, off)
                    if off < 0: break
                    found.append(hex(addr + off)); off += 1
            print('RAMPTR', found[:50], flush=True)
            blk = emu.lib.peek_block(0, 0x02157800, 0x500)
            for i in range(0, 0x500, 0x20):
                ws = [int.from_bytes(blk[i + j:i + j + 4], 'little') for j in range(0, 0x20, 4)]
                print(f'TABLE {0x02157800+i:08x}: ' + ' '.join(f'{w:08x}' for w in ws), flush=True)
        except Exception as e:
            print('RAMPTR ERR', e, flush=True)
    hits.append((src, dst, size, srchead, allregs))
    emu.continue_after_break()

print('hits', len(hits), flush=True)
heads = []
for src, dst, size, srchead, regs in hits[:40]:
    try:
        head = emu.lib.peek_block(0, dst, 16).hex()
    except Exception as e:
        head = 'ERR:' + str(e)
    heads.append(head)
for i, ((src, dst, size, srchead, regs), head) in enumerate(zip(hits, heads)):
    print(f'{i:3d} src={src:08x} dst={dst:08x} size={size:08x} srchead={srchead}', flush=True)
    print(f'     regs={" ".join(f"{r:08x}" for r in regs)} dsthead={head}', flush=True)
