# NDS Sonic Collection: MD Emulator Reverse Engineering

This project documents research into the structure and loading chain of the built-in MD/Genesis emulator found in an NDS Sonic collection. **The repository contains only analysis scripts and documentation — no game ROMs, extracted game binaries, or copyrighted assets.**

> You need to supply your own original NDS copy and your own MD game image before using these scripts. The local paths in the scripts are examples only; adjust them to your environment.

## About the Emulator and the Games

**The emulator.** Collection ships with a Sega Mega Drive / Genesis emulator derived from jEnesisDS. It is not a standalone program — its core is a hand-written ARM9 68K threaded interpreter statically linked into the main binary, dispatching through a 65,536-entry opcode table at `0x0202F480`. The 68K CPU core runs on the ARM9; audio (Z80 / YM2612) was not recovered from the ARM9 and is likely handled by the ARM7. The original jEnesisDS is known to cap game ROMs at 3 MB and to have VDP/graphics compatibility gaps with certain titles (community builds such as jEnesisDSPlus address part of this). Our tests confirm this in-collection build applies its own patches to the bundled ROMs.

**The games.** The collection bundles four retail Mega Drive titles — Sonic the Hedgehog, Sonic the Hedgehog 2, Sonic the Hedgehog 3, and Sonic & Knuckles — 2 MB each. They are not stored as plain `.md` files. Each is split into 64 KB pages, compressed with a custom LZ77 variant, and packed into `image/Game.pak` as 128 pages (8 MB including mirrored pages). SEGA rewrote these ROMs for the release — stripping header fields, fixing the `$Axxx/$Fxxx` opcode bug, and removing two-player code — so the extracted images are collection-specific editions, not byte-identical to retail dumps.

**What we did.** We reconstructed the container layout, the custom LZ77 decompression and the real runtime load chain, then tried swapping in other MD ROMs (Sonic 3D Blast, Mortal Kombat). The load chain and data path are fully verified — a foreign ROM header appears in the 68K ROM buffer at `0x02170000` and its code starts executing — but a clean game image is still blocked by the emulator's VDP compatibility and the limited number of mapped pages per game slot. See `REPORT.md` sections 6–9 for the full experiments.

## Key Findings

See [`REPORT.md`](REPORT.md) for full details. Summary:

- The collection does contain a hand-written ARM9 68K interpreter, with its dispatch table at `0x0202F480`.
- Game ROMs are not stored directly in the NDS filesystem. They use a custom LZ77 variant and are decompressed at runtime into the 68K ROM buffer at `0x02170000`.
- The decompressor is at `0x020844B8`; the token length base, back-reference distance and `swab` byte order have all been reconstructed — see `scripts/lz_ccms.py`.
- `Game.pak` holds two consecutive `{addr, size}` tables:
  - T1 @ `0x20B65C0`, 80 entries;
  - T2 @ `0x20B6840`, 24 entries.
  The default centered game actually reads T2 `[16..23]`, which is why earlier injection attempts did nothing and v24 showed a black screen.
- After writing another MD ROM's pages into the correct table entries, a `MORTAL KOMBAT` header appears in the 68K ROM buffer and code starts executing, but display output is still limited by emulator VDP compatibility and the number of mapped pages.

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
| `scripts/inject26.py` ~ `inject28.py` | injection experiments at various stages |
| `scripts/mcp_black_diag.py` | headless boot / black-screen diagnosis via melonds-mcp |
| `scripts/mcp_dumpbuf.py` | dump the 68K ROM buffer and verify its header |
| `scripts/mcp_bp_blockD.py` | decompressor breakpoint tracing |

## How to Use

All scripts are standalone Python files that read local files and write results next to them. **Before running anything, open the script and edit the hardcoded paths at the top** (`ROM`, `NDS`, `MK`, `OUT`, `D`, etc.) to match your own machine. These paths point to the original author's setup and will not work as-is.

### 1. Prepare your files

- A legally owned copy of the original NDS game (the `.nds` used by the scripts).
- Optionally, a legally owned MD/Genesis game image (`.md` / `.bin`) if you want to try an injection experiment.
- If you want to run the headless-debug scripts, build `melonds-mcp` first (see Requirements).

### 2. Extract and inspect the bundled ROMs (no emulator needed)

```bash
python scripts/nds.py            # parse the NDS header, FNT and FAT
python scripts/final_extract.py  # decompress Game.pak into rom_pages/ (page_XXX.swab.bin)
python scripts/split_games.py    # rebuild the 4 MB image and split per-game .md files
python scripts/verify.py         # disassemble page headers with capstone to sanity-check output
```

This path only needs Python (plus `capstone` for `verify.py`). Outputs land in `rom_pages/` and `roms/`.

### 3. Inject a different MD ROM (experimental)

```bash
python scripts/inject22.py   # baseline: writes pages into the @0x5C0 table
python scripts/inject26.py   # corrected: writes into the real table @0x20B6840
python scripts/inject28.py   # all-slot variant
```

Each injector pads the source `.md` to 4 MB, byte-swaps it (swab16), re-compresses the pages with `lz_ccms.py`, and rewrites the appropriate `{addr, size}` table entries in a copy of the NDS ROM. The result is a new `.nds` you can open in an emulator. **Injection is research-only**: as documented in `REPORT.md`, the ROM executes but a clean display has not been achieved.

### 4. Debug with the headless emulator (melonds-mcp required)

```bash
python scripts/mcp_black_diag.py path/to/build.nds  # navigate the menu and capture screenshots
python scripts/mcp_dumpbuf.py    path/to/build.nds  # dump the 68K ROM buffer at 0x02170000
python scripts/mcp_bp_blockD.py  path/to/build.nds  # breakpoint on the decompressor
```

Pass the ROM to inspect as the first argument. These scripts drive melonDS without a GUI, so they work on machines where the emulator window will not open. Screenshots are written to `diag_*/` folders.

### Notes

- Run scripts from the `scripts/` directory, or run them by full path — imports such as `from lz_ccms import ...` assume the script's own folder is on `sys.path` (most injectors add it themselves).
- The paths and addresses in the scripts are specific to the sample documented in `REPORT.md`. A different ROM or regional release will need its own offsets re-derived.
- Always keep a clean copy of the original `.nds`; injectors write a separate output file and should never touch your source.

## Requirements

- Python 3.10+
- Most scripts use only the standard library; `verify.py` needs `capstone`, and early screenshot scripts use Pillow.
- Headless-debug scripts depend on `melonds-mcp` (the `mcp` branch of `sanduyin/melonDS-mcp`) and require you to build the DLL yourself. That dependency is not included here.
