# NDS 索尼克经典合集：MD 模拟器逆向研究

本项目整理了对某 NDS 索尼克经典合集内部 MD/Genesis 模拟器的结构与加载链研究。**仓库只包含分析脚本和文档，不包含任何游戏 ROM、提取出的游戏二进制或受版权保护的素材。**

> 使用前请自行准备一份你合法拥有的原始 NDS 副本，以及一份你合法拥有的 MD 游戏镜像。脚本里的本地路径只是示例，需要按你的环境修改。

## 核心结论

完整细节见 [`REPORT.md`](REPORT.md)。简要结论：

- 合集内确实内置了一个 ARM9 手写汇编的 68K interpreter，派发表位于 `0x0202F480`。
- 游戏 ROM 不是直接放在 NDS 文件系统里，而是经专用 LZ77 变体压缩后，由运行时解压到 68K ROM 缓冲 `0x02170000`。
- 解压器位于 `0x020844B8`；token 长度基数、回溯距离和 `swab` 字节序都已还原，见 `scripts/lz_ccms.py`。
- `Game.pak` 中有两张连续的 `{addr, size}` 表：
  - T1 @ `0x20B65C0`，80 项；
  - T2 @ `0x20B6840`，24 项。
  默认居中游戏实际读取 T2 的 `[16..23]`，这也是早期注入一直无效、v24 黑屏的原因。
- 把另一个 MD ROM 的页写入正确表项后，68K ROM 缓冲能出现 `MORTAL KOMBAT` 头并开始执行，但显示仍受模拟器 VDP 兼容性和映射页数量限制。

## 目录结构

```text
REPORT.md          完整逆向报告
scripts/           全部分析、解压、注入与无头调试脚本（不含游戏数据）
.gitignore         阻止 ROM / 二进制 / 截图被提交
LICENSE            MIT 许可证
```

脚本中常用的几个：

| 文件 | 作用 |
| --- | --- |
| `scripts/nds.py` | 手写 NDS header / FNT / FAT 解析 |
| `scripts/lz_ccms.py` | 合集专用 LZ77 变体的编码/解码 |
| `scripts/final_extract.py` | 从 Game.pak 中提取并解压页面 |
| `scripts/inject26.py` ~ `inject28.py` | 不同阶段的注入实验 |
| `scripts/mcp_black_diag.py` | 使用 melonds-mcp 做无头启动/黑屏诊断 |
| `scripts/mcp_dumpbuf.py` | dump 68K ROM 缓冲并验证头部 |
| `scripts/mcp_bp_blockD.py` | 解压器断点追踪 |

## 环境依赖

- Python 3.10+
- 标准库即可运行大部分脚本；早期截图脚本用到 Pillow。
- 无头调试脚本依赖 `melonds-mcp`（`sanduyin/melonDS-mcp` 的 `mcp` 分支），需自行构建 DLL。该依赖不在本仓库内。

## 合法使用说明

本仓库仅用于个人学习与互操作性研究。请不要把以下内容提交到公开仓库：

- `*.nds` / `*.md` 游戏镜像
- `arm9.bin`、`arm7.bin`、`Game.pak` 等从 ROM 提取的二进制
- 解压后的页面、音频、纹理、截图

`.gitignore` 已做基本拦截，但提交前仍建议 `git status` 人工确认。

## 推送到 GitHub

本仓库已初始化 git。请自行创建空仓库后执行：

```bash
git remote add origin <你的仓库URL>
git branch -M main
git push -u origin main
```

**不要把 Personal Access Token 写进代码、issue 或聊天记录。** 如果 token 曾经明文暴露，请立即在 GitHub 设置中撤销并重新生成。
