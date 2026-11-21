import struct, sys, os, json

class NDS:
    def __init__(self, path):
        self.f = open(path, 'rb')
        self.hdr = self.f.read(0x200)
        self.title = self.hdr[0:12].decode('ascii', 'replace').strip('\0 ')
        self.code = self.hdr[0x0C:0x10].decode('ascii', 'replace')
        self.maker = self.hdr[0x10:0x12].decode('ascii', 'replace')
        r = lambda o: struct.unpack_from('<I', self.hdr, o)[0]
        self.arm9_off = r(0x20); self.arm9_entry = r(0x24); self.arm9_addr = r(0x28); self.arm9_size = r(0x2C)
        self.arm7_off = r(0x30); self.arm7_entry = r(0x34); self.arm7_addr = r(0x38); self.arm7_size = r(0x3C)
        self.fnt_off = r(0x40); self.fnt_size = r(0x44)
        self.fat_off = r(0x48); self.fat_size = r(0x4C)
        self.a9ov_off = r(0x50); self.a9ov_size = r(0x54)
        self.a7ov_off = r(0x58); self.a7ov_size = r(0x5C)
        self.rom_size = r(0x80)
        self.banner_off = r(0x68)
        self.files = []      # (id, path, start, end)
        self.dirs = []
        self._parse_fs()

    def rd(self, off, n):
        self.f.seek(off); return self.f.read(n)

    def _parse_fs(self):
        fnt = self.rd(self.fnt_off, self.fnt_size)
        sub_off = struct.unpack_from('<H', fnt, 0)[0]
        num_dirs = struct.unpack_from('<H', fnt, 2)[0] & 0x0FFF
        self.num_dirs = num_dirs
        dirents = []
        for i in range(num_dirs):
            base = 8 + i * 8
            e_off, first_id = struct.unpack_from('<II', fnt, base)
            dirents.append((e_off, first_id))

        def walk(di, prefix):
            e_off, fid = dirents[di]
            p = sub_off + e_off
            while True:
                if p >= len(fnt): return
                b = fnt[p]; p += 1
                if b == 0: return
                nlen = b & 0x7F
                name = fnt[p:p+nlen].decode('ascii', 'replace'); p += nlen
                if b & 0x80:
                    self.files.append((fid, prefix + name))
                    fid += 1
                else:
                    sub_idx = struct.unpack_from('<H', fnt, p)[0]; p += 2
                    self.dirs.append(prefix + name + '/')
                    walk(sub_idx, prefix + name + '/')

        walk(0, '')
        # FAT
        fat = self.rd(self.fat_off, self.fat_size)
        self.fat = []
        for i in range(len(fat) // 8):
            s, e = struct.unpack_from('<II', fat, i * 8)
            self.fat.append((s, e))

    def file_span(self, fid):
        return self.fat[fid]

    def read_file(self, fid):
        s, e = self.fat[fid]
        if e <= s: return b''
        return self.rd(s, e - s)

    def info(self):
        return dict(title=self.title, code=self.code, maker=self.maker,
                    arm9=(hex(self.arm9_off), hex(self.arm9_addr), self.arm9_size, hex(self.arm9_entry)),
                    arm7=(hex(self.arm7_off), hex(self.arm7_addr), self.arm7_size, hex(self.arm7_entry)),
                    a9ov=(hex(self.a9ov_off), self.a9ov_size), a7ov=(hex(self.a7ov_off), self.a7ov_size),
                    fnt=(hex(self.fnt_off), self.fnt_size), fat=(hex(self.fat_off), self.fat_size),
                    rom_size=self.rom_size, num_dirs=self.num_dirs, num_files=len(self.files))

if __name__ == '__main__':
    rom = NDS(sys.argv[1])
    for k, v in rom.info().items(): print(f'{k}: {v}')
    print('--- files ---')
    for fid, path in sorted(rom.files, key=lambda x: x[1]):
        s, e = rom.file_span(fid)
        print(f'{fid:5d} {s:9d} {e-s:9d}  {path}')
