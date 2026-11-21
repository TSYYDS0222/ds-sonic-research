"""用 melonds-mcp 的 ctypes 绑定实测注入 ROM。"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "melonds-mcp", "mcp", "python"))
from PIL import Image
from melonds_mcp.emulator import EmulatorState

ROM = sys.argv[1] if len(sys.argv) > 1 else "../SCC_extract/roms/MK_v1_clean.nds"
LABEL = sys.argv[2] if len(sys.argv) > 2 else "mk_v1"

emu = EmulatorState()
print("open:", emu.open_rom(os.path.abspath(ROM)), "running:", emu.is_running())
print("rom_info:", emu.lib.rom_info())
print("status:", emu.get_status() if hasattr(emu, "get_status") else emu.lib.get_status())

W, H = 256, 192

def shot(name, frames, skip=False):
    r = emu.advance_frames(frames, skip_render=skip)
    raw = emu.lib.screenshot_bytes()
    top = raw[:W*H*3]; bottom = raw[W*H*3:W*H*6]
    img = Image.new("RGB", (W, H*2))
    img.putdata([tuple(top[i:i+3]) for i in range(0, len(top), 3)] +
                [tuple(bottom[i:i+3]) for i in range(0, len(bottom), 3)])
    p = f"{LABEL}_{name}.png"
    img.save(p)
    print(f"[{name}] frames={r['frames_executed']}/{r['frames_requested']} "
          f"fn={r['frame_number']} running={r['running']} break={r['break_hit']} -> {p}")

# 分阶段截图，观察卡在哪
shot("boot", 60)
shot("s1", 180)
shot("s2", 300)
shot("s3", 600)

# 68K 寄存器组（ARM9 软件模拟，之前分析的 r6 寄存器文件）—— 先 dump ARM9 状态
print("ARM9 regs:", [hex(x) for x in emu.lib.get_registers(0)[:16]])
print("final status:", emu.lib.get_status())
