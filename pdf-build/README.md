# 渊学通雅思暑假封闭营 · PDF 生成工具

本目录用于生成两份 PDF 文档：

1. **渊学通雅思暑假封闭营-内部培训与产品详解手册.pdf**
   - 用途：渊学通顾问内部培训底册
   - 内容：核心痛点 / 销售话术 / 竞品对比 / 产品说明书 / 协同产品
   - 严禁外发

2. **渊学通雅思暑假封闭营-项目介绍-对外资料.pdf**
   - 用途：意向客户咨询时直接发送的项目资料
   - 内容：项目介绍 / 班型设置 / 服务团队 / 一日日程 / 招生信息
   - 已剔除内部销售话术与竞品对比内容

## 文件结构

```
pdf-build/
  ├── internal_manual.html     # 内部手册 HTML 源文件
  ├── external_brochure.html   # 对外资料 HTML 源文件
  ├── build.sh                 # 一键生成 PDF 脚本
  └── README.md                # 本文件
fonts/                          # 中文字体（自动下载，未入库）
pdfs/                           # 生成的 PDF（最终输出）
```

## 一键生成

```bash
bash pdf-build/build.sh
```

脚本会自动：
- 下载思源黑体 / 思源宋体（首次运行时）
- 安装 weasyprint（如未安装）
- 渲染 HTML → PDF 到 `pdfs/` 目录

## 系统依赖

- Python 3.9+
- pango（Linux: `dnf install -y pango` 或 `apt install -y libpango-1.0-0 libpangoft2-1.0-0`）

## 修改内容

直接编辑 `internal_manual.html` 或 `external_brochure.html`，重新运行 `build.sh` 即可。
