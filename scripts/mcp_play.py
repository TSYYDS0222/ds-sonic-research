"""自动导航 melonDS：过语言选择 -> 游戏选择 -> 进入游戏，全程截图。"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "melonds-mcp", "mcp", "python"))
from PIL import Image, ImageDraw
from melonds_mcp.emulator import EmulatorState

ROM = sys.argv[1] if len(sys.argv) > 1 else "../SCC_extract/roms/MK_v1_clean.nds"
LABEL = sys.argv[2] if len(sys.argv) > 2 else "play"
W, H = 256, 192

emu = EmulatorState()
print("open:", emu.open_rom(os.path.abspath(ROM)))

def shot(name):
    raw = emu.lib.screenshot_bytes()
    top = raw[:W*H*3]; bottom = raw[W*H*3:W*H*6]
    img = Image.new("RGB", (W, H*2))
    img.putdata([tuple(top[i:i+3]) for i in range(0, len(top), 3)] +
                [tuple(bottom[i:i+3]) for i in range(0, len(bottom), 3)])
    img.save(f"{LABEL}_{name}.png")
    print(f"  shot {name} -> {LABEL}_{name}.png")

def frames(n):
    emu.advance_frames(n)

def tap(x, y, hold=4, wait=40):
    # touch API uses full-screen coords? set_touch takes likely local screen coords; try lower-screen local
    emu.lib.lib.melonds_input_set_touch_pos(x, y)
    frames(hold)
    emu.lib.lib.melonds_input_release_touch()
    frames(wait)

def press(key, hold=4, wait=30):
    from melonds_mcp.constants import buttons_to_bitmask
    emu.lib.lib.melonds_input_keypad_update(buttons_to_bitmask([key]))
    frames(hold)
    emu.lib.lib.melonds_input_keypad_update(0)
    frames(wait)

frames(60)
shot("00_lang")

# 语言界面: 下屏三个按钮 中文(约y=140) FRANCAIS(约y=163) ESPANOL(约y=182), 下屏局部坐标
# tap_screen 通常需要下屏局部坐标(0..256, 0..192)
print("tap 中文")
emu.lib.lib.melonds_input_set_touch_pos(128, 140)
frames(5); emu.lib.lib.melonds_input_release_touch(); frames(60)
shot("01_after_lang")

print("tap 中文 alt full")
emu.lib.lib.melonds_input_set_touch_pos(128, 140+192)
frames(5); emu.lib.lib.melonds_input_release_touch(); frames(60)
shot("02_after_lang_alt")

# 尝试 A / START
print("press A")
press("a", 5, 60)
shot("03_after_a")

print("press start")
press("start", 5, 60)
shot("04_after_start")

print("final status", emu.lib.get_status())
