import struct
src=open('D:/tsyyds/shijiamoniqi2.11/Sonic 3D Blast (USA, Europe, Korea) (En).md','rb').read()

# Count 16-bit words by high nibble across ROM code region
from collections import Counter
c=Counter()
for i in range(0x200, min(len(src),0x400000)-1, 2):
    w=(src[i]<<8)|src[i+1]
    c[(w>>12)&0xf]+=1
print('high-nibble distribution (first 4MB):')
for n in range(16): print(f'  ${n:x}xxx: {c[n]}')

# Community: emulator treats $Axxx/$Fxxx as $6xxx. Actually likely:
# The emulator's 68K core has a bug/patch where opcode bit patterns are remapped.
# Need to find what the ORIGINAL collection ROMs look like vs standard,
# i.e. did SEGA patch $A/$F opcodes in the game ROMs to $6xxx?
# Check decoded Sonic2 page (real running ROM) for $A/$F opcodes in code region.
p=open('../SCC_extract/rom_pages/page_032.swab.bin','rb').read()  # Sonic2 ROM page 0
c2=Counter()
for i in range(0x200,len(p)-1,2):
    w=(p[i]<<8)|p[i+1]
    c2[(w>>12)&0xf]+=1
print('\nSonic2 decoded page0 high-nibble distribution:')
for n in range(16): print(f'  ${n:x}xxx: {c2[n]}')

# Find what $Axxx opcodes are in Sonic3D - are they real instructions the emulator mis-decodes?
# $Axxx = line 1010 (rarely used) ; $Fxxx = invalid/reserved except F000-F0FF
# Actually in 68000: $Axxx is unimplemented line1010, $Fxxx is invalid.
# The emulator likely maps these to $6xxx (Bcc) to save decode table space.
# Games rarely use them, so patch is safe. But Sonic3D may use $Axxx as traps.
print('\n$Axxx sample words in Sonic3D (first 20 with context):')
cnt=0
for i in range(0x200,min(len(src),0x100000)-1,2):
    w=(src[i]<<8)|src[i+1]
    if (w>>12)==0xa:
        print(f'  @0x{i:x}: {w:04x}  ctx={src[i-4:i+8].hex()}')
        cnt+=1
        if cnt>=20:break
print('total $A words in first 1MB:',sum(1 for i in range(0x200,min(len(src),0x100000)-1,2) if ((src[i]<<8)|src[i+1])>>12==0xa))
print('total $F words in first 1MB:',sum(1 for i in range(0x200,min(len(src),0x100000)-1,2) if ((src[i]<<8)|src[i+1])>>12==0xf))
