import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'melonds-mcp', 'mcp', 'python'))
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask

ROM = os.path.abspath(sys.argv[1])
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
tap(225, 185, 8, 30)
emu.advance_frames(300)

print('ROM', os.path.basename(ROM), 'status', emu.lib.get_status(), flush=True)
base = 0x02170000
size = 0x10000
data = bytearray()
for off in range(0, size, 0x1000):
    data += emu.lib.peek_block(0, base + off, 0x1000)
def swab(b):
    return bytes(x for p in zip(b[1::2], b[0::2]) for x in p)

print('buf first 64:', data[:64].hex(), flush=True)
print('swab header 0x100:', swab(data[0x100:0x140]), flush=True)
for kw in (b'SEGA GENESIS', b'SEGA MEGA DRIVE', b'MORTAL', b'Mortal', b'SONIC', b'ESAG', b'AEGIS'):
    hits = []
    p = 0
    while True:
        p = data.find(kw, p)
        if p < 0: break
        hits.append(hex(base + p)); p += 1
    print(kw, len(hits), hits[:10], flush=True)
