"""CCMS 解压器 —— 从 ARM9 0x020844B8 逐行翻译。"""
import struct, sys

def swpb(b):
    """ARM swpb: 读内存的字节做字节序反转(此处等价于 byteswap 单个字节? 实为半字交换的一部分).
    从汇编看 swpb r6,r6,[r1] 把 r6 低字节写入 dst, 同时把 dst 原值读入 r6.
    但输出是 swab 的 ROM, 说明数据本身以大端字节对存储. 先按字面实现, 验证后调整.
    """
    return b

def decompress(src, expected_len=None):
    p = 0
    hdr = struct.unpack_from('<I', src, p)[0]; p += 4
    r2 = hdr >> 8                 # 剩余输出字节数
    mode = hdr & 0xF
    out = bytearray()
    lr = 0
    bitcount = 0
    while r2 > 0:
        if bitcount == 0:
            lr = src[p]; p += 1
            bitcount = 8
        bit = (lr >> 7) & 1
        lr = (lr << 1) & 0xFF
        bitcount -= 1
        if bit == 0:
            # 字面量: ldrb r6,[r0],#1; swpb r6,r6,[r1]
            r6 = src[p]; p += 1
            out.append(r6)
            r2 -= 1
        else:
            # token
            r5 = src[p]  # ldrb r5,[r0]  (不递增)
            if mode == 0:
                r6 = 3
            else:
                if (r5 & 0xE0) != 0:
                    r6 = 1
                else:
                    p += 1
                    r6 = r5 & 0xF
                    r6 <<= 4
                    if (r5 & 0x10):
                        r6 <<= 8
                        r5 = src[p]; p += 1
                        r6 += (r5 << 4)
                        r6 += 0x100
                    r6 += 0x11
                    r5 = src[p]  # ldrb r5,[r0]  (下面 add r0,#1)
            # add r3, r6, r5 asr #4  -> 长度
            r3 = r6 + (r5 >> 4)
            p += 1
            r5 = r5 & 0xF
            ip = (r5 << 8)
            r6 = src[p]; p += 1
            r5 = r6 | ip          # 距离 base
            ip = r5 + 1
            r2 -= r3
            # 回溯拷贝: ldrb r5,[r1,-ip]; swpb r5,r5,[r1]; dst++; r3--
            for _ in range(r3):
                idx = len(out) - ip
                val = out[idx] if idx >= 0 else 0
                out.append(val)
    return bytes(out)

if __name__ == '__main__':
    nds = open('D:/tsyyds/shijiamoniqi2.11/56dfeb171d434dd37ad3336586ac026ebd309a4b84f37f7773257695ad9cfa91.nds','rb').read()
    B = 0x20f7000
    blob = nds[B:]
    out = decompress(blob)
    print('decompressed len', len(out), 'hdr', hex(struct.unpack_from('<I',blob)[0]))
    print('first 0x40:', out[:0x40].hex())
    # 运行时 RAM 的 Sonic1 ROM
    ram = open('arm9_ram_at_game.bin','rb').read()
    rt = ram[0x2170000-0x2000000:0x2170000-0x2000000+len(out)]
    print('runtime  0x40:', rt[:0x40].hex())
    print('MATCH?', out == rt)
    # 找第一个不同
    if out != rt:
        for i,(a,b) in enumerate(zip(out,rt)):
            if a!=b:
                print('first diff at',hex(i),'dec',hex(a),'rt',hex(b));break
