# Sonic Classic Collection (NDS) — Reverse-Engineering Report of the Built-in MD Emulator

**Sample**: `56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds`
**ROM info**: title `SONICCOLLECT`, game code `VSOE`, publisher code `8P`, size 64 MiB (67,108,864 bytes)
**Bottom line**: the game does contain a complete Mega Drive / Genesis emulator. Its core is a pure ARM-assembly, 64K-dispatch-table-driven threaded 68K interpreter, statically linked into the ARM9 main program rather than shipped as a separate module. The ROM compression format inside `Game.pak` has also been fully reverse-engineered, yielding disassemblable 68K code.

---

## 1. Container Structure

NDS standard header (0x200 bytes) parse results:

| Section | File offset | Load address | Size |
|---|---|---|---|
| ARM9 | 0x004000 | 0x02004000 | 537,728 B |
| ARM7 | 0x087600 | 0x02380000 | 175,896 B |
| FNT | 0x0B2600 | — | 202 B |
| FAT | 0x0B2800 | — | 72 B (9 entries) |
| Banner | 0x0B2A00 | — | — |

No overlays (`arm9_ov=0`, `arm7_ov=0`), so **all logic lives in that 525 KB ARM9 binary**.

The filesystem holds only 9 files across two directories (root + `image/`):

```
0  snd_Sonic1_sfx.mods     787,052
1  snd_Sonic1_trx.mods   3,175,796
2  snd_Sonic2_sfx.mods   1,282,444
3  snd_Sonic2_trx.mods   5,881,932
4  snd_Sonic3_sfx.mods   2,338,684
5  snd_Sonic3_trx.mods  12,412,000
6  title.wav               580,488
7  image/Game.pak        5,355,024   <- ROM archive
8  image/screensGame_us.dat 14,928,384
```

---

## 2. Where the Emulator Lives

### 2.1 Fingerprint: a 65,536-entry 68K instruction dispatch table

Scanning the ARM9 for arrays whose consecutive 32-bit words all point into the code region gives exactly one hit:

```
address 0x0202F480 .. 0x0206F47F   65,536 entries x 4 B = 256 KB
```

65,536 = 2^16, exactly the full space of one 68000 instruction word (16 bits). **This is an `opcode -> handler` jump table.**

The table contains only 1,458 unique targets, all within `0x020111DC .. 0x0202F47F` (~123 KB) — that is the entire handler code of the 68K interpreter. The most frequent target is `0x0202EF08` (15,526 times), the "unimplemented / illegal" fallback.

### 2.2 Main dispatch loop (threaded interpreter)

Every handler ends with these three instructions:

```asm
ldrh  fp, [sl], #2          ; fetch next 68K opcode, PC += 2
sub   r7, r7, #0x40000      ; charge 4 cycles (16.16 fixed point, i.e. 4<<16)
ldr   pc, [sb, fp, lsl #2]  ; jump to the handler indexed by the opcode
```

`ldr pc, [...]` rewrites PC directly to dispatch — classic **threaded code**, with no switch statement and no central dispatch loop. `sb` is the base address of the table above (0x0202F480).

### 2.3 Register conventions (confirmed empirically)

| ARM register | Purpose |
|---|---|
| `r6` | 68K register file: `D0-D7` at `+0x00..0x1C`, `A0-A7` at `+0x20..0x3C` |
| `r7` | Cycle-budget counter (16.16 fixed point; each instruction subtracts `cycles<<16`) |
| `r8` | Host base address of the current 64 KB page (used for address translation) |
| `sb` | Base of the 68K dispatch table, 0x0202F480 |
| `sl` | 68K PC (a byte pointer into host memory, not a 68K linear address) |
| `fp` | The 16-bit opcode just fetched |

### 2.4 Spot checks (all three match the expected semantics)

**NOP `0x4E71`** -> `0x0202E570`
```asm
ldrh fp,[sl],#2 ; sub r7,r7,#0x40000 ; ldr pc,[sb,fp,lsl#2]
```
= does nothing, charges 4 cycles, fetches the next instruction. Correct.

**MOVEQ `0x7000`** -> `0x0202E57C`
```asm
and  r2, fp, #0xe00      ; bits 9-11 = destination data register
lsls r1, fp, #0x18       ; extract the low-byte immediate
asr  r1, r1, #0x18       ; sign-extend to 32 bits
str  r1, [r6, r2, lsr #7]; store into Dn
orrmi r7,r7,#8 ; orreq r7,r7,#4   ; set N/Z flags from the result
```
= `MOVEQ #imm,Dn`, including N/Z flags. Correct.

**RTS `0x4E75`** -> `0x0202E1F8`
```asm
ldr  r0, [r6, #0x3c]     ; A7
add  r3, r0, #4
str  r3, [r6, #0x3c]     ; A7 += 4
add  r0, r8, r0, lsr #16 ; (addr & 0xFFFF) + current page base -> read return address
ldrh r1,[r0],#2 ; ldrh r3,[r0] ; orr r1,r3,r1,lsl#16   ; fetch 32 bits
bic  r2, r1, #0xff000000 ; 24-bit address
ldr  r0, [r6, #0x68]
ldr  r0, [r0, r2, lsr #16 ...]   ; look up the 64 KB page table with addr>>16
```
= `RTS`, and it exposes the key design: **the 68K 24-bit address space is split into 64 KB pages, with the page table hung off `[r6+0x68]`**. Both instruction fetches and data accesses go through this page mapping.

### 2.5 This clue, in turn, pinned down Game.pak

The page size is 64 KB. And `image/Game.pak` contains exactly **128 entries x 64 KB = 8 MB** of blocks — meaning:

> `Game.pak` = 128 64 KB pages of the 68K address space (the ROM area), decompressed/swapped into memory on demand.

The archive also stores four game-name strings right near the front:
```
0x20B6900  "SONIC THE HEDGEHOG 2"
0x20B6918  "SONIC THE HEDGEHOG 3"
0x20B6930  "SONIC THE HEDGEHOG"
0x20B6944  "SONIC & KNUCKLES"
```
Four games x 2 MB (including padding) = 8 MB, matching the 128 pages exactly.

---

## 3. Internal Structure of Game.pak

```
+0x000  u32  6                     ; purpose undetermined
+0x004  u32  0x023D7410
+0x008  128 x {u32 pak_offset, u32 stored_size}   ; exactly fills the data area, 4-byte aligned padding
+0x900  four game-name strings + zero padding
+0x800..0x50FFF   other metadata
+0x51000 .. end    actual data of the 128 blocks (packed back to back, no holes)
```

Of the 128 blocks:
- **45 are stored raw** (`stored_size == 0x10000`, one 64 KB page stored directly)
- **83 are compressed**, every one starting with `11 00 00 01`, i.e. the Nintendo DS `LZ77 (type 0x11)` header, declaring a decompressed size of `0x10000` bytes

---

## 4. Solved: the Game.pak Decompression Algorithm (the breakthrough this round)

The previous round was stuck here. This round located the decompressor in the ARM9 at `0x2004DF4` and fully reconstructed it:

**Algorithm = standard Nintendo LZ77 (type 0x11) + a preset 64 KB zero dictionary + 16-bit byte swapping**

```python
# Each page is 64KB; block header 11 00 00 01 (type=0x11, decompressed size=0x10000)
# Key: the back-reference base must include a 64KB preset zero window, not start at 0
size = blob[1] | blob[2]<<8 | blob[3]<<16   # = 0x10000
out = bytearray(); sp = 4; win = bytes(0x10000)   # preset zero dictionary
while len(out) < size:
    flags = blob[sp]; sp += 1
    for bit in range(7, -1, -1):
        if flags & (1<<bit):                 # compressed token
            b0, b1 = blob[sp], blob[sp+1]; sp += 2
            n = (b0 >> 4) + 3                # length +3
            D = (((b0 & 0xF) << 8) | b1) + 1 # distance +1
            src = 0x10000 + len(out) - D     # <- key: +64KB zero dictionary
            for k in range(n):
                j = src + k
                out.append(win[j] if j < 0x10000 else out[j-0x10000])
        else:                                # literal
            out.append(blob[sp]); sp += 1
page = swab16(out)   # swap every two bytes: 00 01 -> 01 00
```

**Why it failed before**: the dictionary start was computed as `len(out) - D`, but it should be `0x10000 + len(out) - D`. The first 64 KB of this LZ window is an implicit all-zero dictionary (the uninitialized area of the emulator's page table), so early tokens reference the zero window rather than being "out-of-range back-references". Adding that 64 KB makes every compressed page decode in one pass.

**Byte order**: ROM data inside the archive is stored 16-bit byte-swapped (this is why `ESAG` was found instead of `SEGA`). After decompression, adjacent bytes must be swapped back to obtain standard 68K byte order. Verification: page 32, once swabbed, disassembles into perfectly valid Sonic 2 code (`4a78ffe8 tst.w` / `6704 beq.b` / `4e75 rts` / `b0fcb000 cmpa.w`), and yields the ROM header `SP=00FFFFFE, PC=00000206` plus the title string `(C)SEGA 1992.SEPSONIC THE HEDGEHOG 2`.

**Page mirroring**: among the 128 table entries there are 86 unique offsets; `i` and `i+64` frequently point at the same block — this is the mirrored mapping of the Mega Drive 4 MB address space, so the real ROM is only **4 MB = 64 pages**.

**Caveat**: SEGA modified these ROMs (confirmed by the community) — removing some standard header fields, fixing jEnesisDS's bug of executing `$Axxx/$Fxxx` as `$6xxx`, and stripping two-player-mode code. The extracted images are therefore "collection-specific editions" and not byte-identical to retail `.md` dumps.

---

## 5. Deliverables

```
SCC_extract/
|-- files/                       # 9 internal files, extracted verbatim
|   |-- Game.pak                 (5,355,024 B)
|   |-- screensGame_us.dat       (14,928,384 B)
|   |-- snd_Sonic{1,2,3}_{sfx,trx}.mods
|   |-- title.wav
|   `-- _manifest.txt
|-- emulator/                    # emulator core (see above)
|   |-- ...
|   `-- game_pak_chunks.txt
|-- rom_pages/                   # newly added this round: 128 decompressed pages
|   |-- page_000.swab.bin ... page_127.swab.bin   # 64 KB each, swabbed, ready to disassemble
|   `-- rom_all_8mb.swab.bin     # full 8 MB image (including mirror redundancy)
`-- roms/                        # newly added this round: split 4 MB game images
    |-- combined_4mb.swab.bin    # deduplicated real 4 MB ROM
    `-- game_{0,1,2,3}_xMB.md    # 1 MB per chunk (community ROM header was rewritten; research only)
```

**Reproduction scripts** (in `work/`): `final_extract.py` (decompress + swab), `split_games.py` (split), `verify.py` (disassembly check). The core decompressor is at ARM9 `0x2004DF4`, with parameters `len=(b0>>4)+3, disp=12bit+2` (reverse-scan version); the pak pages use forward BIOS semantics `disp=12bit+1`.

**How to use**: in Ghidra create a new raw binary, set Language to `ARM:LE:32:v5` and Base to `0x02004000`, then import `arm9.bin`. Jump to `0x0202F480` for the dispatch table; `0x0202E570` onward holds the high-frequency handlers for NOP / RTS / MOVEQ.

---

## 6. ROM Injection (vA/vB failed; v3-v6 pending testing)

**Important correction (second pass)**: vA/vB got stuck on the loading screen. Root cause identified — they wrote the new ROM into `GP+0x51000` (= `0x2107000` inside the pak), which **falls inside Sonic 1's CCMS blob (0x20f7000, 0x80000 bytes)**, effectively overwriting the original game data and guaranteeing a load failure.

The real data structures (clarified in the second pass):

- Each game is described by a **descriptor** (6 of them, stride **0x48**; CRC@+0x08, size@+0x0c, CCMS blob base@+0x2c), with key fields `size@+0xc` and `base@+0x2c`.
- `base` points to a **CCMS blob**, formatted `[crc32]["CCMS"][ver=0x02027b11][gameid][swab ROM]`. This is the actual entry point the emulator uses to load a game ROM; the 7 blobs are at 0x20f7000 / 0x2197000 / 0x2267000 / 0x2347000 / 0x2357000 / 0x2367000 / 0x2377000.
- The `@0x8 / @0x5c0` page tables edited earlier are **not** the game-ROM load entry point (they are the runtime 68K page mapping).
- The CRC in the CCMS header is **not** standard crc32 / adler / md5 (exhaustively tested, no match); it may be a content ID or not verified at all.

Outputs are in `roms/`, in recommended order:

- **`Sonic3D_v6_slot5.nds`** <- first choice: minimal change, directly overwrites the 4 MB empty slot `0x2377000` (descriptor slot5, gameid=0x500), preserving the CCMS header and all original structure.
- `Sonic3D_v5_full.nds` — new data placed in the 12 MB free tail area; page tables and all 6 descriptors redirected.
- `Sonic3D_v4_desc4m.nds` — free-area data plus descriptor size changed to 4 MB.
- `Sonic3D_v3_safe.nds` — most conservative: free-area data + page tables only, never touching the original pak.
- `Sonic3D_vA_keepdesc.nds` / `vB_size4m.nds` — older versions (known failures, kept for the record).

### Injection principle

Original belief (vA/vB, wrong): editing the two page tables to point at raw pages was enough; in reality the data landed inside the CCMS blob.

Second-pass understanding:
1. Pad the `.md` to 4 MB -> swap adjacent bytes (swab16).
2. Depending on the variant: v6 overwrites the data area of the slot5 CCMS blob; v3-v5 write to the 12 MB free area at the ROM's tail (`0x3420000` onward, 64 KB aligned, touching no original data).
3. The descriptor stride is **0x48** (not the earlier misjudged 0x3c), with `size@+0xc` and `base@+0x2c`.
4. The CCMS blob header is 16 bytes: `{u32 crc} "CCMS" {u32 ver=0x02027b11} {u32 gameid}`.

### Injection principle (simpler than expected: no compressor needed)

It was initially assumed an LZ77 encoder had to be implemented — it **does not**. In the original pak, 47 of 128 entries are **raw pages** with `size == 0x10000`; the emulator maps these directly into 68K RAM without decompression. So all that is needed is:

1. Pad the `.md` to 4 MB (64 pages x 64 KB) and swap adjacent bytes (swab16).
2. Write these 64 pages into the pak data area starting at `GP+0x51000`.
3. Rebuild both page tables (pak+0x8 and pak+0x5c0, 128 entries each of `{addr, size}`): entry `i` points to page `i & 63` with `size = 0x10000` (mirror pages 64-127 reuse the first 64 pages).
4. Rename the four game names starting at pak+0x900 to `SONIC 3D BLAST`.

**Final confirmation of page-table entry semantics**: `addr` is the absolute address of the block within the NDS ROM (`0x02107000` = start of the pak data area; raw-page addresses advance in strict 0x10000 steps), and `size == 0x10000` denotes a raw page mapped directly. This was inferred and confirmed from the raw-page address distribution in the original pak (consecutive steps starting at 0x20b7000).

### Verification results

- The 4 MB image rebuilt from the injected page table is **byte-for-byte identical** to the source `.md` (`verify_inject.py`).
- Recovered the `SEGA GENESIS` header @0x100 and title `SONIC 3D BLAST DIRECTOR'S CUT` (a modified ROM).
- All 128 page-table entries point to the correct raw pages; the swab round-trip is consistent.

**Verification not performed**: the current environment cannot launch melonDS (the GUI process will not start in the sandbox), so no real-device screenshots were taken. The data path (swab, page tables, descriptors) is statically proven consistent, but the following can only be confirmed on real hardware:
- Whether the CCMS header CRC is actually verified (algorithm not recovered; v6 fills in the crc32 of the new data)
- Whether the emulator applies opcode patches to `$Axxx/$Fxxx` (the community has confirmed the collection ROMs were rewritten)

**Recommended testing order**: v6 (minimal change) -> v5 (full redirection) -> v4 -> v3. If all get stuck loading, it is almost certainly a CCMS CRC check or opcode-patch issue, and the CCMS load function must be dug out of the ARM9.

**Reproduction scripts** (`work/`): `inject6.py`/`inject5.py`/`inject3.py`/`inject2.py` (variants), `pak_struct.py`/`real_tables.py`/`locate_fields.py`/`blob_verify.py`/`crc_final.py` (format analysis).

---

## 7. Next Steps (ordered by cost/benefit)

1. **Verify injected ROMs on real hardware**: open vA / vB in melonDS on a machine that can run the GUI and see whether the game starts. If the screen goes black, suspect descriptor verification and `$Axxx/$Fxxx` opcode patching first.
2. **Z80 / YM2612**: there is no 256-entry jump table in the ARM9; audio most likely resides in the ARM7 (`arm7.bin`, 175 KB) or in an ARM9 switch statement, and can be dug out separately.
3. **Game-header repair**: the header fields rewritten by SEGA can be copied back from a retail `.md` to produce an image that runs directly in standard emulators.

---

## 8. Pinning Down the Load Chain with the melonds-mcp Headless Debugger (major breakthrough this round)

Built `sanduyin/melonDS-mcp` (MinGW toolchain, DLL `libmelonds_mcp.dll`), gaining 62 debugging tools and no longer depending on blind user testing. Key empirical findings:

**All previous injection versions overturned**: comparing runtime RAM of the original and injected builds shows they are identical — injections from vA through v20 never actually took effect. Every earlier "it enters the game" result was the original Sonic running.

**The real game-ROM load chain (confirmed with breakpoints + write watchpoints)**:
1. Startup reads the **`@0x5C0` table** (Game.pak+0x5C0, 104 valid entries, format `{addr,size}`) — not the `@0x8` table.
2. slot0(S1)=entries 0-31, slot1(S2)=32-63, slot2(S3)=64-95, slot3(S&K)=96-103. (The game list defaults to centering on Sonic 3.)
3. Each entry points to a compressed block -> copied to RAM `0x02160000` -> decompressor **`0x020844B8`** -> written into the 68K ROM buffer `0x02170000`.
4. Decompressor algorithm (reconstructed instruction by instruction from ARM disassembly): a DS LZ77 variant with header `11 xx xx xx` (len<<8|0x11), flags MSB-first; **token length L=1+(b0>>4)** (not the standard +3); back-reference D=((b0&0xF)<<8|b1)+1; writes use `swpb` -> **the decompressed result must be in swab form**.
5. The decoder was cross-validated against real blocks from the original Sonic 3 (`lz_ccms.py`) and reproduces `ESAG G NESESI`.

**Final injectors `inject22.py` / `inject24.py`**:
- Trim MK to 2 MB -> opcode patch (high nibble A/E/F -> 6) -> swab each 64 KB page -> compress with `lz_ccms.encode`
- Modify only the `@0x5C0` table to point at the new data (free tail area `0x19F1000`, ~7 MB), leaving names/descriptors untouched
- Static verification: page 0, once decompressed and swabbed, gives `SP=ffff0200 PC=00000200` and `SEGA GENESIS`; emulator breakpoint confirms that at the moment of decompression the destination bytes are `ffff0002...` = the MK header — the data path is 100% open.

**Empirical progress**:
- v22 (slot2 modified): after starting the default Sonic 3 slot, PC keeps changing (68K executing normally), passes the SEGA logo and reaches the level screen (with graphical corruption) — the ROM is being read and executed, but the display layer mixes in original UI content.
- v23 (+opcode patch): turned the dead-loop PC `0xFFFF0104` into a normal `0x202EF34`, proving the patch works.
- v24 (all slots overwritten): reached the Sonic 3 playable menu (ATRAS/CARGAR/GUARDAR/PAUSA), the deepest progress so far.

**Remaining issue**: the display output is still dominated by the collection UI / original Sonic 3 assets; no pure MK screen was obtained. Possible causes: the collection binds each of the four game ROMs' display to its own descriptor / CCMS thumbnail; or the jEnesisDS core has insufficient VDP timing compatibility with MK (its README admits "some games have abnormal graphics" and will not be fixed). Resolving this requires continuing to trace 68K PC / VDP writes with the debugger and is no longer solvable by static injection alone.

**New artifacts**: `roms/MK_v22_final.nds` (correct-mechanism baseline), `MK_v23_opcode.nds` (with opcode patch), `MK_v24_allslots.nds` (all slots overwritten); scripts `work/lz_ccms.py` (exact decompressor reconstruction + encoder), `inject22/23/24.py`, `mcp_*.py` (headless-debugger test scripts). The DLL is in `work/melonds-mcp/build/mcp-direct/`.

---

## 9. Black-Screen Root Cause: We Had Been Editing the Wrong Table; the Real Load Table Located

The user reported v24 as "stuck on a black screen". Reproducing it with the melonds-mcp adaptive navigator showed:

- After startup v24 is a single flat color across the whole screen (top_mean=1.3) — genuinely black.
- v22/v23 never loaded MK at all: the header of the runtime 68K ROM buffer `0x02170000` is still `SEGA MEGA DRIVE ... SONIC THE HEDGEHOG`, meaning the first 80 entries of `Game.pak+0x5C0` edited earlier are not the ROM table used by the default game.
- Setting a breakpoint at the decompressor `0x020844B8` and reading registers/memory traced the first runtime page source to `0x01A34EE8`, which is exactly the MK page-8 compressed block we wrote; working backward from this revealed the real table location.

**The real table structure (two contiguous tables inside Game.pak)**:
- T1 @ `0x20B65C0`: 80 entries, block sizes of 32/16/16/16 pages, but editing it does not affect the default game's ROM.
- T2 @ `0x20B6840`: 24 entries (previously mistaken for entries 80-103 of T1). **The default centered game reads T2[16..23], 8 pages total**, each decompressed into one 64 KB page of the 68K ROM buffer.

**v27/v28 fixes**:
- `inject26/27/28.py` write MK page0..7 into `T2[16..23]`.
- Runtime verification: `0x02170100` holds `ESAG` (swabbed SEGA); once swabbed it reads `SEGA GENESIS (C)T-81 1993.SEP MORTAL KOMBAT` — the MK ROM is genuinely loaded.
- v27/v28 no longer die at `0xFFFF0104`; the ARM9 enters a 68K interpreter handler (`0x0202E33C` -> `0x0202E27C` -> `0x02011118`), showing MK code has begun executing.

**Still unresolved**: the screen remains black. The default slot provides only 8 x 64 KB pages (512 KB), while MK is 2 MB; and jEnesisDS's VDP/DMA support for MK is insufficient. The opcode-patched v29 hangs even earlier and was abandoned. Switching games left/right still runs the original Sonic 2 / Sonic 3, proving T1 is not the ROM load table.

**New deliverables**: `roms/MK_v27_offset16.nds` (minimal correct modification), `roms/MK_v28_realtable_all.nds` (full-table overwrite); scripts `work/inject26.py` through `inject28.py`, `work/mcp_black_diag.py`, `work/mcp_bp_blockD.py`, `work/mcp_dumpbuf.py`.

---

## 10. User Decided to Stop Injection and Restore the Original Data

The user explicitly stated: "Drop Mortal Kombat, switch back to the original data." The original ROM was never modified:
`D:/tsyyds/shijiamoniqi2.11/56dfeb...nds`, size 67,108,864 bytes, SHA-256 `56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91` (matching the filename).

An unmodified clean copy has been placed at `roms/Sonic_Collection_original.nds` and verified to have the same hash. No further MK injection work will be done.
