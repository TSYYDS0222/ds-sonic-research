# Sonic Classic Collection (NDS) — 官方 MD 模拟器逆向提取报告

**样本**：`56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds`
**ROM 信息**：标题 `SONICCOLLECT`，游戏码 `VSOE`，发行商码 `8P`，大小 64 MiB (67,108,864 B)
**结论一句话**：游戏内部**确实自带一套完整的 Mega Drive / Genesis 模拟器**，主体是一段纯 ARM 汇编、64K 派发表驱动的 68K 线程式解释器，编译链接在 ARM9 主程序里，不是独立模块。Game.pak 的 ROM 压缩格式也已完全破解并还原出可反汇编的 68K 代码。

---

## 1. 容器结构

NDS 标准头（0x200 字节）解析结果：

| 段 | 文件偏移 | 装载地址 | 大小 |
|---|---|---|---|
| ARM9 | 0x004000 | 0x02004000 | 537,728 B |
| ARM7 | 0x087600 | 0x02380000 | 175,896 B |
| FNT | 0x0B2600 | — | 202 B |
| FAT | 0x0B2800 | — | 72 B (9 项) |
| Banner | 0x0B2A00 | — | — |

无 overlay（`arm9_ov=0`, `arm7_ov=0`），所以**全部逻辑都在那 525 KB 的 ARM9 里**。

文件系统只有 9 个文件，两个目录（根 + `image/`）：

```
0  snd_Sonic1_sfx.mods     787,052
1  snd_Sonic1_trx.mods   3,175,796
2  snd_Sonic2_sfx.mods   1,282,444
3  snd_Sonic2_trx.mods   5,881,932
4  snd_Sonic3_sfx.mods   2,338,684
5  snd_Sonic3_trx.mods  12,412,000
6  title.wav               580,488
7  image/Game.pak        5,355,024   ← ROM 包
8  image/screensGame_us.dat 14,928,384
```

---

## 2. 模拟器在哪儿

### 2.1 指纹：65536 项的 68K 指令派发表

在 ARM9 里扫描"连续 32 位字全部落在代码区"的数组，只有一处命中：

```
地址 0x0202F480 .. 0x0206F47F   65536 项 × 4 B = 256 KB
```

65536 = 2^16，正好是一条 68000 指令字（16 bit）的全空间。**这是一张 `opcode → handler` 的跳转表。**

表里只有 1458 个唯一目标，全部落在 `0x020111DC .. 0x0202F47F`（约 123 KB）——那就是 68K 解释器的全部处理器代码。最高频的目标是 `0x0202EF08`（15,526 次），是"未实现/非法"兜底。

### 2.2 分派主循环（线程式解释器）

任意一个处理器的结尾都是这三条：

```asm
ldrh  fp, [sl], #2          ; 取下一条 68K 指令字，PC 自增 2
sub   r7, r7, #0x40000      ; 扣 4 个周期（16.16 定点，即 4<<16）
ldr   pc, [sb, fp, lsl #2]  ; 以 opcode 为索引跳转到对应处理器
```

`ldr pc, [...]` 直接改写 PC 做分派 —— 典型的 **threaded code**，没有 switch、没有循环分发。`sb` 就是上表的基址（0x0202F480）。

### 2.3 寄存器约定（实测确认）

| ARM 寄存器 | 用途 |
|---|---|
| `r6` | 68K 寄存器组：`D0–D7` 在 `+0x00..0x1C`，`A0–A7` 在 `+0x20..0x3C` |
| `r7` | 周期预算计数器（16.16 定点，每条指令扣 `周期<<16`） |
| `r8` | 当前 64 KB 页的宿主基址（地址翻译用） |
| `sb` | 68K 派发表基址 0x0202F480 |
| `sl` | 68K PC（宿主内存里的字节指针，不是 68K 线性地址） |
| `fp` | 当前取到的 16 位 opcode |

### 2.4 抽样验证（三条都能对上语义）

**NOP `0x4E71`** → `0x0202E570`
```asm
ldrh fp,[sl],#2 ; sub r7,r7,#0x40000 ; ldr pc,[sb,fp,lsl#2]
```
= 什么也不做，扣 4 周期，取下一条。正确。

**MOVEQ `0x7000`** → `0x0202E57C`
```asm
and  r2, fp, #0xe00      ; 取 bit9-11 = 目标数据寄存器号
lsls r1, fp, #0x18       ; 取低字节立即数
asr  r1, r1, #0x18       ; 符号扩展到 32 位
str  r1, [r6, r2, lsr #7]; 写进 Dn
orrmi r7,r7,#8 ; orreq r7,r7,#4   ; 按结果置 N/Z
```
= `MOVEQ #imm,Dn`，含 N/Z 标志。正确。

**RTS `0x4E75`** → `0x0202E1F8`
```asm
ldr  r0, [r6, #0x3c]     ; A7
add  r3, r0, #4
str  r3, [r6, #0x3c]     ; A7 += 4
add  r0, r8, r0, lsr #16 ; (addr & 0xFFFF) + 当前页基址 → 读返回地址
ldrh r1,[r0],#2 ; ldrh r3,[r0] ; orr r1,r3,r1,lsl#16   ; 取 32 位
bic  r2, r1, #0xff000000 ; 24 位地址
ldr  r0, [r6, #0x68]
ldr  r0, [r0, r2, lsr #16 ...]   ; 用 addr>>16 查 64KB 页表，取新页基址
```
= `RTS`，并且暴露出关键设计：**68K 的 24 位地址空间被切成 64 KB 页，页表挂在 `[r6+0x68]`**。取指、取数都走这套页映射。

### 2.5 这条线索反过来锁定了 Game.pak

页大小 64 KB。而 `image/Game.pak` 里正好是 **128 条 × 64 KB = 8 MB** 的块 —— 也就是说：

> `Game.pak` = 68K 地址空间的 128 个 64 KB 页（ROM 区），按需解压/交换进内存。

包里开头还直接放着 4 个游戏名的字符串：
```
0x20B6900  "SONIC THE HEDGEHOG 2"
0x20B6918  "SONIC THE HEDGEHOG 3"
0x20B6930  "SONIC THE HEDGEHOG"
0x20B6944  "SONIC & KNUCKLES"
```
4 款游戏 × 2 MB（含填充）= 8 MB，和 128 页完全吻合。

---

## 3. Game.pak 的内部结构

```
+0x000  u32  6                     ; 用途未定
+0x004  u32  0x023D7410
+0x008  128 × {u32 pak_offset, u32 stored_size}   ; 恰好铺满整个数据区，4 字节对齐补白
+0x900  4 个游戏名字符串 + 零填充
+0x800..0x50FFF  其它元数据
+0x51000 .. 末尾   128 个块的实际数据（逐块铺满，无空洞）
```

128 块中：
- **45 块原样存储**（`stored_size == 0x10000`，一页 64 KB 直存）
- **83 块压缩存储**，块首一律是 `11 00 00 01`，即 Nintendo DS 的 `LZ77 (type 0x11)` 头，声明解压后 `0x10000` 字节

---

## 4. ✅ 已解决：Game.pak 的解压算法（本次突破）

上一版卡在这里，本次从 ARM9 里定位到解压函数 `0x2004DF4`，彻底还原：

**算法 = 标准 Nintendo LZ77（type 0x11）+ 预置 64KB 零字典 + 16 位字节交换**

```python
# 每页 64KB，块首 11 00 00 01 (type=0x11, 解压尺寸=0x10000)
# 关键：回溯基址要加上 64KB 预置零窗口，而不是从 0 开始
size = blob[1] | blob[2]<<8 | blob[3]<<16   # = 0x10000
out = bytearray(); sp = 4; win = bytes(0x10000)   # 预置零字典
while len(out) < size:
    flags = blob[sp]; sp += 1
    for bit in range(7, -1, -1):
        if flags & (1<<bit):                 # 压缩 token
            b0, b1 = blob[sp], blob[sp+1]; sp += 2
            n = (b0 >> 4) + 3                # 长度 +3
            D = (((b0 & 0xF) << 8) | b1) + 1 # 距离 +1
            src = 0x10000 + len(out) - D     # ← 关键：+64KB 零字典
            for k in range(n):
                j = src + k
                out.append(win[j] if j < 0x10000 else out[j-0x10000])
        else:                                # 字面量
            out.append(blob[sp]); sp += 1
page = swab16(out)   # 每两个字节交换：00 01 -> 01 00
```

**为什么之前失败**：字典起点算成了 `len(out) - D`，实际应为 `0x10000 + len(out) - D`。
这个 LZ 的窗口前 64KB 是隐含的全零字典（模拟器页表未初始化区），所以早期 token 会
引用到零窗口，而不是"回溯距离越界"。补上这 64KB 后，全部压缩页一次解通。

**字节序**：包内 ROM 是 16 位交换存放的（这就是之前搜到 `ESAG` 而非 `SEGA` 的原因），
解压后必须逐字节对交换才是标准 68K 字节序。验证：page32 swab 后反汇编出完美合法的
Sonic 2 代码（`4a78ffe8 tst.w` / `6704 beq.b` / `4e75 rts` / `b0fcb000 cmpa.w`），
并还原出 ROM 头 `SP=00FFFFFE, PC=00000206` 和标题串 `(C)SEGA 1992.SEPSONIC THE HEDGEHOG 2`。

**页镜像**：128 个表项里有 86 个唯一偏移，`i` 与 `i+64` 大量指向同一块——这是
Mega Drive 4MB 地址空间的镜像映射，真实 ROM 只有 **4MB = 64 页**。

**仍需注意**：SEGA 改写过这些 ROM（社区已证实）——去掉了部分标准头字段、
修正了 jEnesisDS 把 `$Axxx/$Fxxx` 当 `$6xxx` 执行的 bug、并移除了双人模式相关代码。
所以解出的镜像是"合集专用版"，与零售版 `.md` 不完全一致。

---

## 5. 交付物

```
SCC_extract/
├─ files/                       # 9 个内部文件，原样解出
│   ├─ Game.pak                 (5,355,024 B)
│   ├─ screensGame_us.dat       (14,928,384 B)
│   ├─ snd_Sonic{1,2,3}_{sfx,trx}.mods
│   ├─ title.wav
│   └─ _manifest.txt
├─ emulator/                    # 模拟器核心（见上）
│   ├─ ...
│   └─ game_pak_chunks.txt
├─ rom_pages/                   # ✅ 本次新增：128 页解压结果
│   ├─ page_000.swab.bin ... page_127.swab.bin   # 每页 64KB，已 swab，可直接反汇编
│   └─ rom_all_8mb.swab.bin     # 8MB 全镜像（含镜像冗余）
└─ roms/                        # ✅ 本次新增：切分出的 4MB 游戏镜像
    ├─ combined_4mb.swab.bin    # 去重后的真实 4MB ROM
    └─ game_{0,1,2,3}_xMB.md    # 每 1MB 一块（社区 ROM 头被改写，仅作研究）
```

**复现脚本**（在 `work/`）：`final_extract.py`（解压+swab）、`split_games.py`（切分）、
`verify.py`（反汇编验证）。核心解压器在 ARM9 `0x2004DF4`，参数 `len=(b0>>4)+3, disp=12bit+2`
（反向扫描版本）；pak 页用的是正向 BIOS 语义 `disp=12bit+1`。

**怎么用**：Ghidra 新建 raw binary，Language 选 `ARM:LE:32:v5`,Base 填 `0x02004000`，导入 `arm9.bin`；然后跳到 `0x0202F480` 就是派发表，`0x0202E570` 起是 NOP/RTS/MOVEQ 这些高频处理器。

---

## 6. ROM 注射（vA/vB 失败，v3–v6 待实测）

**重要更正（第二轮）**：vA/vB 卡在加载画面，根因已定位——它们把新 ROM 写进了
`GP+0x51000`（= pak 内部 `0x2107000`），而这个地址**正好落在 Sonic1 的 CCMS blob
（0x20f7000, 0x80000 字节）内部**，等于覆盖了原游戏数据，必然加载失败。

真正的数据结构（第二轮查清）：

- 每个游戏由一个 **descriptor**（6 个，步长 **0x48**；CRC@+0x08、size@+0x0c、
  CCMS blob 基址@+0x2c）描述，字段：`size@+0xc`、`base@+0x2c`
- `base` 指向 **CCMS blob**，格式 `[crc32]["CCMS"][ver=0x02027b11][gameid][swab ROM]`，
  这才是模拟器加载游戏 ROM 的入口；7 个 blob 在 0x20f7000 / 0x2197000 / 0x2267000 /
  0x2347000 / 0x2357000 / 0x2367000 / 0x2377000
- 之前改的 `@0x8 / @0x5c0` 两组页表**不是**游戏 ROM 加载入口（是运行时 68K 页映射）
- CCMS 头的 CRC **不是**标准 crc32/adler/md5（穷举未匹配），可能是内容 ID 或不校验

产出在 `roms/`，按推荐顺序：

- **`Sonic3D_v6_slot5.nds`** ← 首选：最小改动，直接覆盖 4 MB 空槽 `0x2377000`
  （descriptor slot5, gameid=0x500），保留 CCMS 头和所有原结构
- `Sonic3D_v5_full.nds` — 新数据放 12 MB 尾部空闲区，页表 + 6 个 descriptor 全部重定向
- `Sonic3D_v4_desc4m.nds` — 空闲区数据 + descriptor size 改 4 MB
- `Sonic3D_v3_safe.nds` — 最保守：仅空闲区数据 + 页表，完全不碰原 pak
- `Sonic3D_vA_keepdesc.nds` / `vB_size4m.nds` — 旧版（已知失败，仅留档）

### 注射原理

原始认知（vA/vB，错误）：以为改两组页表指向裸页即可，实际写进了 CCMS blob 内部。

第二轮认知：
1. `.md` 补齐 4 MB → 逐字节对交换（swab16）
2. 视变体不同：v6 覆盖 slot5 CCMS blob 的数据区；v3–v5 写到 ROM 尾部 12 MB 空闲区
   （`0x3420000` 起，64K 对齐，不碰任何原数据）
3. descriptor 步长是 **0x48**（不是早期误判的 0x3c），`size@+0xc`、`base@+0x2c`
4. CCMS blob 头 16 字节：`{u32 crc} "CCMS" {u32 ver=0x02027b11} {u32 gameid}`

### 注射原理（比预想简单：不需要写压缩器）

之前以为必须实现 LZ77 编码器，实际**不需要**——原 pak 里 47/128 项是
`size == 0x10000` 的**裸页**（raw page），模拟器直接把它们映射到 68K RAM，不走解压。
所以只要：

1. `.md` 补齐到 4 MB（64 页 × 64 KB），逐字节对交换（swab16）
2. 写进 pak 数据区 `GP+0x51000` 起的 64 页
3. 重建两组页表（pak+0x8、pak+0x5c0，各 128 项 `{addr, size}`）：
   表项 `i` 指向第 `i & 63` 页，`size = 0x10000`（镜像区页 64–127 复用前 64 页）
4. 把 pak+0x900 起的 4 个游戏名改成 `SONIC 3D BLAST`

**页表项语义最终确认**：`addr` 是块在 NDS ROM 里的绝对地址（`0x02107000` = pak
数据区起点，裸页 addr 严格 0x10000 步进），`size == 0x10000` 表示裸页直映射。
这一点由原 pak 的裸页 addr 分布（0x20b7000 起连续步进）反推确认。

### 验证结果

- 从注入后页表重建的 4 MB 镜像与源 `.md` **逐字节一致**（`verify_inject.py`）
- 还原出 `SEGA GENESIS` 头 @0x100、标题 `SONIC 3D BLAST DIRECTOR'S CUT`（这是一款改版 ROM）
- 页表 128 项全部指向正确裸页，swab 往返一致

**未做的验证**：当前环境无法启动 melonDS（GUI 进程在沙箱里起不来），没做实机截图。
数据链路（swab、页表、descriptor）已静态证明一致，但以下只能在真机确认：
- CCMS 头 CRC 是否校验（算法未解出，v6 填的是新数据的 crc32）
- 模拟器是否对 `$Axxx/$Fxxx` 打 opcode 补丁（社区证实合集 ROM 被改写过）

**实测顺序建议**：v6（最小改动）→ v5（全重定向）→ v4 → v3。若全部卡加载，
则几乎可以确定是 CCMS CRC 校验或 opcode 补丁问题，需从 ARM9 里挖 CCMS 加载函数。

**复现脚本**（`work/`）：`inject6.py`/`inject5.py`/`inject3.py`/`inject2.py`（各变体）、
`pak_struct.py`/`real_tables.py`/`locate_fields.py`/`blob_verify.py`/`crc_final.py`（格式分析）。

---

## 7. 下一步（按性价比排序）

1. **实机验证注射 ROM**：在能跑 GUI 的机器上用 melonDS 打开 vA / vB，看是否进游戏。
   若黑屏，优先怀疑 descriptor 校验与 `$Axxx/$Fxxx` opcode 修补。
2. **Z80 / YM2612**：ARM9 里没有 256 项跳转表，音源大概率在 ARM7（`arm7.bin`，175 KB）
   或 ARM9 的 switch 里，可以单独再挖。
3. **游戏头修复**：SEGA 改写的头字段可从零售版 `.md` 复制回来，以生成能在标准模拟器
   直接运行的镜像。

---

## 8. 用 melonds-mcp 无头调试器彻底定位加载链（本轮重大突破）

编译了 `sanduyin/melonDS-mcp`（MinGW 工具链，DLL `libmelonds_mcp.dll`），获得 62 个调试工具，
不再依赖用户盲测。关键实测结论：

**推翻此前所有注入版本**：对比原版与注入版的运行时 RAM，完全一致——
vA~v20 的注入从未真正生效。此前"能进游戏"跑的都是原版 Sonic。

**真正的游戏 ROM 加载链（断点 + 写监视点实测）**：
1. 启动读 **`@0x5C0` 表**（Game.pak+0x5C0，104 项有效，格式 {addr,size}）——不是 `@0x8` 表。
2. slot0(S1)=项0-31, slot1(S2)=32-63, slot2(S3)=64-95, slot3(S&K)=96-103。
   （游戏列表默认居中选中 Sonic3）
3. 每项指向一个压缩块 → 搬到 RAM `0x02160000` → 解压器 **`0x020844B8`** → 写入 68K ROM 缓冲 `0x02170000`。
4. 解压器算法（逐条 ARM 反汇编还原）：DS LZ77 变体，头 `11 xx xx xx`（len<<8|0x11），
   flags MSB-first；**token 长度 L=1+(b0>>4)**（不是标准 +3）；
   回溯 D=((b0&0xF)<<8|b1)+1；写入用 `swpb` → **解压结果需为 swab 形式**。
5. 用原版 Sonic3 真实块交叉验证了解码器（`lz_ccms.py`），能还原 `ESAG G NESESI`。

**最终注入器 `inject22.py` / `inject24.py`**：
- 裁剪 MK 到 2MB → opcode 补丁（高 nibble A/E/F→6）→ 每 64KB 页 swab → `lz_ccms.encode` 压缩
- 只改 `@0x5C0` 表指向新数据（尾部空闲区 `0x19F1000`，约 7MB），不碰名字/descriptor
- 静态验证：page0 解压后 swab 得 `SP=ffff0200 PC=00000200`、`SEGA GENESIS`；
  模拟器断点实测：解压瞬间 dst 字节 `ffff0002...` = MK 头，数据链路 100% 打通。

**实测进展**：
- v22（改 slot2）：默认 Sonic3 槽启动后 PC 持续变化（68K 正常执行），过了 SEGA 标志进到
  关卡画面（带花屏）——ROM 被读取执行，但显示层混有原版 UI 内容。
- v23（+opcode 补丁）：把死循环 PC `0xFFFF0104` 变成正常 `0x202EF34`，证明补丁有效。
- v24（全槽覆盖）：进到 Sonic3 可玩菜单（ATRAS/CARGAR/GUARDAR/PAUSA），是最深进度。

**遗留**：显示输出仍以合集 UI/原版 Sonic3 素材为主，未得到纯 MK 画面。
可能原因：合集把 4 游戏 ROM 的显示与各自 descriptor/CCMS 缩略图绑定；或 jEnesisDS 内核
对 MK 的 VDP 时序兼容不足（README 已承认"部分游戏图形显示不正常"不修）。
这需要继续用调试器跟 68K PC / VDP 写入，已非静态注入可解决。

**新增产物**：`roms/MK_v22_final.nds`（机制正确的基础版）、`MK_v23_opcode.nds`（含 opcode 补丁）、
`MK_v24_allslots.nds`（全槽覆盖）；脚本 `work/lz_ccms.py`（解压器精确还原+编码器）、
`inject22/23/24.py`、`mcp_*.py`（无头调试器实测脚本）。DLL 在
`work/melonds-mcp/build/mcp-direct/`。

---

## 9. 黑屏根因：此前一直改错了表；已定位真正加载表

用户反馈 v24「卡黑屏」。用 melonds-mcp 自适应导航复现后发现：

- v24 启动后整屏单色（top_mean=1.3），确实黑屏。
- v22/v23 根本没加载 MK：运行时 68K ROM 缓冲 `0x02170000` 的头部仍是
  `SEGA MEGA DRIVE ... SONIC THE HEDGEHOG`，说明此前改的 `Game.pak+0x5C0`
  前 80 项不是默认游戏使用的 ROM 表。
- 在解压器 `0x020844B8` 下断点 + 读寄存器/内存，追踪到运行时第一页源为
  `0x01A34EE8`，正好是我们写入的 MK 第 8 页压缩块；由此反推出真正表位置。

**真正的表结构（Game.pak 内两张连续表）**：
- T1 @ `0x20B65C0`：80 项，块大小 32/16/16/16 页，但改它不影响默认游戏 ROM。
- T2 @ `0x20B6840`：24 项（之前被误当成 T1 的第 80~103 项）。
  **默认居中选中游戏读取 T2[16..23] 共 8 页**，每页解压到 68K ROM 缓冲的一个 64KB 页。

**v27/v28 修正**：
- `inject26/27/28.py` 把 MK page0..7 写到 `T2[16..23]`。
- 运行时验证：`0x02170100` 处为 `ESAG`（swab 的 SEGA），swab 后读到
  `SEGA GENESIS (C)T-81 1993.SEP MORTAL KOMBAT`，MK ROM 已真正载入。
- v27/v28 不再死在 `0xFFFF0104`；ARM9 进入 68K interpreter handler
  （`0x0202E33C`→`0x0202E27C`→`0x02011118`），说明 MK 代码开始执行。

**仍未解决**：屏幕仍黑。默认槽只给 8 个 64KB 页（512KB），MK 是 2MB；
且 jEnesisDS 的 VDP/DMA 对 MK 兼容不足。opcode 补丁版 v29 会更早卡住，已弃用。
左右切换游戏仍跑原版 Sonic2/Sonic3，证明 T1 不是 ROM 加载表。

**新增交付**：`roms/MK_v27_offset16.nds`（最小正确修改）、
`roms/MK_v28_realtable_all.nds`（全表覆盖）；脚本 `work/inject26.py`~`inject28.py`、
`work/mcp_black_diag.py`、`work/mcp_bp_blockD.py`、`work/mcp_dumpbuf.py`。

---

## 10. 用户决定停止注入，恢复原始数据

用户明确表示「不要真人快打了，换回原始数据」。原始 ROM 从未被改动：
`D:/tsyyds/shijiamoniqi2.11/56dfeb...nds`，大小 67,108,864 字节，
SHA-256 `56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91`（与文件名一致）。

已在 `roms/Sonic_Collection_original.nds` 放置一份未经修改的干净拷贝并校验哈希一致。
后续不再继续 MK 注入工作。

---

*本报告仅针对用户自有的游戏转储做结构与兼容性研究，不包含任何 ROM 数据分发。*
