import os, sys, struct, zlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'melonds-mcp', 'mcp', 'python'))
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask

ROOT = os.path.dirname(__file__)
TAG = os.path.splitext(os.path.basename(sys.argv[1]))[0] if len(sys.argv) > 1 else 'MK_v24_allslots'
OUT = os.path.join(ROOT, 'diag_' + TAG)
os.makedirs(OUT, exist_ok=True)
ROM = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.abspath(os.path.join(ROOT, '..', 'SCC_extract', 'roms', 'MK_v24_allslots.nds'))

emu = EmulatorState()
print('rom', ROM, 'opened', emu.open_rom(ROM), flush=True)


def save_png(path, width, height, rgb):
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(chunk(b'IHDR', ihdr))
        f.write(chunk(b'IDAT', zlib.compress(bytes(raw), 6)))
        f.write(chunk(b'IEND', b''))


def top_stats():
    raw = emu.lib.screenshot_bytes()[:256 * 192 * 3]
    return sum(raw) / len(raw), len(set(tuple(raw[i:i + 3]) for i in range(0, len(raw), 3)))


def wait_until_mainmenu(max_frames=1200):
    for _ in range(max_frames // 10):
        mean, colors = top_stats()
        if mean > 100 and colors > 1000:
            return True
        emu.advance_frames(10)
    return False


def shot(tag):
    raw = emu.lib.screenshot_bytes()
    top = raw[:256 * 192 * 3]
    bot = raw[256 * 192 * 3:]
    path = os.path.join(OUT, tag + '.png')
    save_png(path, 256, 384, top + bot)
    save_png(os.path.join(OUT, tag + '_top.png'), 256, 192, top)
    save_png(os.path.join(OUT, tag + '_bot.png'), 256, 192, bot)
    mean_top = sum(top) / len(top)
    uniq_top = len(set(tuple(top[i:i + 3]) for i in range(0, len(top), 3)))
    st = emu.lib.get_status()
    print(f'{tag}: frame={st[1]} arm9pc={st[6]:08x} arm7pc={st[7]:08x} '
          f'top_mean={mean_top:.1f} top_colors={uniq_top} shot={path}', flush=True)


def tap(x, y, hold=8, wait=40):
    emu.lib.lib.melonds_input_set_touch_pos(x, y)
    emu.advance_frames(hold)
    emu.lib.lib.melonds_input_release_touch()
    emu.advance_frames(wait)


def key(k, hold=5, wait=25):
    emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask([k]))
    emu.advance_frames(hold)
    emu.lib.lib.melonds_input_keypad_update(0)
    emu.advance_frames(wait)


# Boot and menu stages (adaptive: wait until each screen actually changes)
emu.advance_frames(60); shot('00_boot')
tap(128, 140, 10, 90); shot('01_after_tap140')
key('a', 5, 60)
print('wait main menu ->', wait_until_mainmenu(), flush=True)
shot('02_mainmenu')
tap(128, 49, 8, 50); emu.advance_frames(20); shot('03_list')
sel = os.environ.get('SEL', '')
if sel == 'right':
    key('right', 5, 30)
elif sel == 'left':
    key('left', 5, 30)
elif sel == 'tapright':
    tap(195, 100, 8, 40)
elif sel == 'tapleft':
    tap(60, 100, 8, 40)
shot('03b_selected')
# Launch selected game button
tap(225, 185, 8, 30); emu.advance_frames(200); shot('04_launch_200')
for n in (120, 240, 360, 600, 900):
    emu.advance_frames(n)
    shot(f'05_after_{n}')
    regs = emu.lib.get_registers(0)
    print('  arm9 regs r0-r11:', ' '.join(f'{r:08x}' for r in regs[:12]), flush=True)
