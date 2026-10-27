#!/usr/bin/env bash
# 从页面实际用字生成霞鹜文楷子集，避免改文案后回退到系统字体。
#
# 用法：
#   ./scripts/subset-font.sh
#
# 依赖：fonttools + brotli（提供 pyftsubset）
#   python3 -m venv .venv && .venv/bin/pip install fonttools brotli
#   PATH="$PWD/.venv/bin:$PATH" ./scripts/subset-font.sh
#
# 源字体默认从 jsDelivr 下载到 .fonts/（已在 .gitignore 中），
# 也可以用 FONT_SRC=/path/to/LXGWWenKai-Regular.woff2 指定本地文件。
set -euo pipefail

cd "$(dirname "$0")/.."

SRC="${FONT_SRC:-.fonts/LXGWWenKai-Regular.woff2}"
SRC_URL="https://cdn.jsdelivr.net/npm/@fontsource/lxgw-wenkai@5.3.0/files/lxgw-wenkai-latin-500-normal.woff2"
OUT="assets/fonts/wenkai-subset.woff2"
CHARS=".fonts/chars.txt"

if ! command -v pyftsubset >/dev/null 2>&1; then
  echo "找不到 pyftsubset。请先安装：python3 -m venv .venv && .venv/bin/pip install fonttools brotli" >&2
  echo "然后把 .venv/bin 加入 PATH 再运行本脚本。" >&2
  exit 1
fi

if [ ! -f "$SRC" ]; then
  echo "下载源字体 → $SRC"
  mkdir -p .fonts
  curl -fL --retry 3 --max-time 300 -o "$SRC" "$SRC_URL"
fi

mkdir -p .fonts

# 收集全站 HTML 的可见文字（去掉 script/style/注释/标签），
# 再加上 ASCII 与常用标点，避免遗漏。
python3 - "$CHARS" <<'PY'
import html
import pathlib
import re
import sys

out = pathlib.Path(sys.argv[1])
skip = {".git", ".tmp", ".fonts", ".venv", "_site", "node_modules"}
files = [
    p for p in sorted(pathlib.Path(".").rglob("*.html"))
    if not (set(p.parts) & skip)
]
chars = set()

for name in files:
    text = pathlib.Path(name).read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<(script|style)\b.*?</\1>", "", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = html.unescape(text)
    chars.update(ch for ch in text if not ch.isspace())

# 页面可能由脚本写入或作为回退字体使用的字符
chars.update("晝夜")
chars.update(chr(c) for c in range(0x20, 0x7F))
chars.update("　、。，．；：？！…—·「」『』《》〈〉（）【】“”‘’↗↑→↓")

out.write_text("".join(sorted(chars)), encoding="utf-8")
print(f"字符数：{len(chars)} → {out}")
PY

pyftsubset "$SRC" \
  --text-file="$CHARS" \
  --flavor=woff2 \
  --layout-features='kern,liga,vert,vrt2' \
  --no-hinting \
  --desubroutinize \
  --output-file="$OUT"

echo "已生成 $OUT（$(wc -c < "$OUT") 字节）"
