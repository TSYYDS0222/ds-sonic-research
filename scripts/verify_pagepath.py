import struct,os,re

# Verify: how does decoded page32 (Sonic2 ROM header) map to page table entry?
GP=0x20b6000
d=open('D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds','rb').read()

# decoded page32 is ROM page 0 -> which table entry has size that decompresses to it?
# The decompressor dictionary trick produced 128 pages; find which raw compressed chunk
# at page-table entry produced page 32 with the SEGA header.
# From decode_all.py, pages were generated in table entry order i=0..127.
# So page_032.bin corresponds to table entry i=32.
for tbl in (0x8,0x5c0):
    a,s=struct.unpack_from('<II',d,GP+tbl+32*8)
    print(f'tbl{tbl:x}[32]: addr={a:x} size={s:x} (blob? {0x2197000<=a<0x2297000})')
    data=d[a:a+s]
    print('  chunk head:',data[:24].hex(),' type byte=',hex(data[0]))
