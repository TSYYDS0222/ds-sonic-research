# NDS Sonic Collection: Reverse Engineering the Built-in MD Emulator

This project documents research into the structure and loading chain of the built-in MD/Genesis emulator in an NDS Sonic collection. **The repository contains only analysis scripts and documentation — no game ROMs, extracted binaries, or copyrighted assets.**

> Before using these scripts, you need to supply your own legally owned copy of the original NDS game and, for injection experiments, an MD game image. The local paths in the scripts are examples only; update them to match your setup.

## About the Emulator and the Games

**The emulator.** The collection ships with a Sega Mega Drive / Genesis emulator derived from jEnesisDS. It is not a standalone program: its core is a hand-written ARM9 68K threaded interpreter statically linked into the main binary, with instruction dispatch handled by a 65,536-entry opcode table at `0x0202F480`. The 68K CPU core runs on the ARM9; we did not locate the audio side (Z80 / YM2612) in the ARM9 code, so it is most likely handled by the ARM7. The original jEnesisDS has a known 3 MB limit on game ROMs and documented VDP/graphics compatibility issues with some titles; community builds such as jEnesisDSPlus address part of this. Our tests confirm that this bundled build applies its own patches to the included ROMs.

**The games.** The collection includes four retail Mega Drive titles — Sonic the Hedgehog, Sonic the Hedgehog 2, Sonic the Hedgehog 3, and Sonic & Knuckles — each 2 MB. They are not stored as plain `.md` files. Instead, each game is split into 64 KB pages, compressed with a custom LZ77 variant, and packed into `image/Game.pak` as 128 pages (8 MB including mirrored pages). SEGA rewrote these ROMs for the release: it stripped some header fields, fixed the `$Axxx/$Fxxx` opcode bug, and removed two-player code. The extracted images are therefore collection-specific editions and are not byte-identical to retail dumps.

**What we did.** We reconstructed the container layout, the custom LZ77 decompression, and the real runtime load chain, then tried replacing the bundled games with other MD ROMs (Sonic 3D Blast and Mortal Kombat). The load chain and data path are fully verified: a foreign ROM header appears in the 68K ROM buffer at `0x02170000` and its code begins executing. However, a clean game image has not been achieved due to the emulator's VDP compatibility issues and the limited number of pages mapped to each game slot. See `REPORT.md`, sections 6–9, for the full experiments.

## Key Findings

See [`REPORT.md`](REPORT.md) for full details. Summary:

- The collection does contain a hand-written ARM9 68K interpreter, with its dispatch table at `0x0202F480`.
- Game ROMs are not stored directly in the NDS filesystem. They use a custom LZ77 variant and are decompressed at runtime into the 68K ROM buffer at `0x02170000`.
- The decompressor is at `0x020844B8`. Its token length base, back-reference distance, and `swab` byte order have all been reconstructed — see `scripts/lz_ccms.py`.
- `Game.pak` contains two consecutive `{addr, size}` tables: T1 @ `0x20B65C0` (80 entries) and T2 @ `0x20B6840` (24 entries). The default centered game reads T2 `[16..23]`, which is why earlier injection attempts had no effect and v24 produced a black screen.
- After writing another MD ROM's pages into the correct table entries, a `MORTAL KOMBAT` header appears in the 68K ROM buffer and the code begins to execute. However, the display is still limited by the emulator's VDP compatibility and the number of mapped pages.

## Layout

```text
REPORT.md          full reverse-engineering report
scripts/           all analysis, extraction, injection and headless-debug scripts (no game data)
.gitignore         blocks ROMs / binaries / screenshots from being committed
LICENSE            MIT license
```

Commonly used scripts:

| File | Purpose |
| --- | --- |
| `scripts/nds.py` | hand-written NDS header / FNT / FAT parser |
| `scripts/lz_ccms.py` | encoder/decoder for the collection-specific LZ77 variant |
| `scripts/final_extract.py` | extract and decompress pages from Game.pak |
| `scripts/inject26.py` – `inject28.py` | injection experiments at various stages |
| `scripts/mcp_black_diag.py` | headless boot / black-screen diagnosis via melonds-mcp |
| `scripts/mcp_dumpbuf.py` | dump the 68K ROM buffer and verify its header |
| `scripts/mcp_bp_blockD.py` | decompressor breakpoint tracing |

## How to Use

All scripts are standalone Python files that read local files and write their output alongside them. **Before running a script, open it and edit the hardcoded paths near the top** (`ROM`, `NDS`, `MK`, `OUT`, `D`, etc.) to match your machine. These paths point to the original author's setup and will not work as-is.

### 1. Prepare your files

- A legally owned copy of the original NDS game (the `.nds` referenced by the scripts).
- Optionally, a legally owned MD/Genesis game image (`.md` / `.bin`) if you want to try an injection experiment.
- If you plan to use the headless-debug scripts, build `melonds-mcp` first (see Requirements).

### 2. Extract and inspect the bundled ROMs (no emulator needed)

```bash
python scripts/nds.py            # parse the NDS header, FNT and FAT
python scripts/final_extract.py  # decompress Game.pak into rom_pages/ (page_XXX.swab.bin)
python scripts/split_games.py    # rebuild the 4 MB image and split per-game .md files
python scripts/verify.py         # disassemble page headers with capstone to sanity-check output
```

This workflow only requires Python (plus `capstone` for `verify.py`). Output files are written to `rom_pages/` and `roms/`.

### 3. Inject a different MD ROM (experimental)

```bash
python scripts/inject22.py   # baseline: writes pages into the @0x5C0 table
python scripts/inject26.py   # corrected: writes into the real table @0x20B6840
python scripts/inject28.py   # all-slot variant
```

Each injector pads the source `.md` to 4 MB, byte-swaps it (swab16), recompresses the pages with `lz_ccms.py`, and rewrites the appropriate `{addr, size}` entries in a copy of the NDS ROM. The result is a new `.nds` file that you can open in an emulator. **Injection is research-only**: as documented in `REPORT.md`, the ROM executes, but a clean display has not been achieved.

### 4. Debug with the headless emulator (melonds-mcp required)

```bash
python scripts/mcp_black_diag.py path/to/build.nds  # navigate the menu and capture screenshots
python scripts/mcp_dumpbuf.py    path/to/build.nds  # dump the 68K ROM buffer at 0x02170000
python scripts/mcp_bp_blockD.py  path/to/build.nds  # breakpoint on the decompressor
```

Pass the ROM you want to inspect as the first argument. These scripts drive melonDS without a GUI, so they also work on machines where the emulator window will not open. Screenshots are written to `diag_*/` folders.

### Notes

- Run the scripts from the `scripts/` directory or by full path. Imports such as `from lz_ccms import ...` assume the script's own folder is on `sys.path` (most injectors add that folder themselves).
- The paths and addresses in the scripts are specific to the sample described in `REPORT.md`. With a different ROM or regional release, you will need to re-derive the offsets.
- Always keep a clean copy of the original `.nds`. The injectors write a separate output file and never modify your source.

## Requirements

- Python 3.10+
- Most scripts use only the standard library; `verify.py` requires `capstone`, and the early screenshot scripts use Pillow.
- The headless-debug scripts depend on `melonds-mcp` (the `mcp` branch of `sanduyin/melonDS-mcp`) and require you to build the DLL yourself. That dependency is not included here.
