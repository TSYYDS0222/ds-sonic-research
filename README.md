# NDS Sonic Collection: MD Emulator Reverse Engineering

This project documents research into the structure and loading chain of the built-in MD/Genesis emulator found in an NDS Sonic collection. **The repository contains only analysis scripts and documentation — no game ROMs, extracted game binaries, or copyrighted assets.**

> You need to supply your own original NDS copy and your own MD game image before using these scripts. The local paths in the scripts are examples only; adjust them to your environment.

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

## Requirements

- Python 3.10+
- Most scripts use only the standard library; early screenshot scripts use Pillow.
- Headless-debug scripts depend on `melonds-mcp` (the `mcp` branch of `sanduyin/melonDS-mcp`) and require you to build the DLL yourself. That dependency is not included here.
