import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'melonds-mcp', 'mcp', 'python'))
from melonds_mcp.emulator import EmulatorState
from melonds_mcp.constants import buttons_to_bitmask
ROM = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.abspath('../SCC_extract/roms/MK_probe_blockD.nds')
emu = EmulatorState(); emu.open_rom(ROM)
wp = emu.lib.lib.melonds_debug_wp_add(0, 0x023D1004, 4, 2)
print('wp', wp, flush=True)
emu.advance_frames(400)
ev = emu.lib.wp_events(max_events=256)
print('events', len(ev), flush=True)
for e in ev[:100]:
    print('  pc=%08x addr=%08x kind=%s size=%s value=%08x' % (e['pc'], e['address'], e['kind'], e['size'], e['value']), flush=True)
