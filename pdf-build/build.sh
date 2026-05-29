#!/usr/bin/env bash
# 一键生成两份PDF（内部手册 + 对外资料）
# 依赖：python3、weasyprint、pango
# 用法：bash pdf-build/build.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FONT_DIR="$ROOT/fonts"
OUT_DIR="$ROOT/pdfs"
BUILD_DIR="$ROOT/pdf-build"

mkdir -p "$FONT_DIR" "$OUT_DIR"

# 1. 下载中文字体（如不存在）
download() {
  local url="$1"; local out="$2"
  if [ ! -f "$out" ]; then
    echo "==> 下载字体 $(basename "$out") ..."
    curl -k -L -o "$out" "$url"
  fi
}
download "https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf" "$FONT_DIR/NotoSansSC-Regular.otf"
download "https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Bold.otf"    "$FONT_DIR/NotoSansSC-Bold.otf"
download "https://github.com/notofonts/noto-cjk/raw/main/Serif/OTF/SimplifiedChinese/NotoSerifCJKsc-Bold.otf"  "$FONT_DIR/NotoSerifSC-Bold.otf"

# 2. 安装 weasyprint（如未安装）
if ! python3 -c "import weasyprint" 2>/dev/null; then
  echo "==> 安装 weasyprint ..."
  pip install weasyprint
fi

# 3. 生成 PDF
echo "==> 生成《内部培训与产品详解手册》..."
python3 -c "
from weasyprint import HTML
HTML('$BUILD_DIR/internal_manual.html').write_pdf('$OUT_DIR/渊学通雅思暑假封闭营-内部培训与产品详解手册.pdf')
"

echo "==> 生成《项目介绍-对外资料》..."
python3 -c "
from weasyprint import HTML
HTML('$BUILD_DIR/external_brochure.html').write_pdf('$OUT_DIR/渊学通雅思暑假封闭营-项目介绍-对外资料.pdf')
"

echo
echo "完成。PDF已生成至：$OUT_DIR/"
ls -la "$OUT_DIR/"
