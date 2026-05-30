# PaperBridge

PaperBridge 是一个 CLI-first 的论文 PDF 结构化转换工具。第一版面向有文本层的学术论文 PDF，将输入 PDF 转换为统一的 `document_json`，再导出 JSON、Markdown、TXT、DOCX 和独立图片资源。

## 功能范围

- 支持有文本层的英文论文 PDF。
- 输出 `paper.json`、`paper.md`、`paper.txt`、`paper.docx`、`summary.json`。
- 渲染页面截图到 `assets/pages/`。
- 尝试裁剪图片和表格区域到 `assets/figures/`、`assets/tables/`。
- 识别基础结构：标题、摘要、章节、正文、图注、表格标题、参考文献、页眉页脚候选。
- 检测无文本层页面并记录 warning，不做 OCR。
- 支持 OpenAI 兼容 LLM/VLM 接口，失败时自动降级到规则解析。

## 安装与开发

```bash
uv sync --extra dev
uv run paperbridge --help
```

## CLI

```bash
paperbridge convert paper.pdf --out output/
paperbridge inspect paper.pdf
paperbridge validate output/paper.json
paperbridge export output/paper.json --formats md,txt,docx
```

常用转换参数：

```bash
paperbridge convert INPUT_PDF \
  --out output \
  --formats json,md,txt,docx \
  --dpi 200 \
  --max-pages 5 \
  --use-llm \
  --use-vlm \
  --debug \
  --force \
  --json
```

## LLM / VLM 配置

PaperBridge 使用 OpenAI 兼容接口，通过环境变量配置：

```bash
export PAPERBRIDGE_OPENAI_API_KEY="..."
export PAPERBRIDGE_OPENAI_BASE_URL="https://api.example.com/v1"
export PAPERBRIDGE_LLM_MODEL="your-text-model"
export PAPERBRIDGE_VLM_MODEL="your-vision-model"
```

如果启用 `--use-llm` 或 `--use-vlm` 但配置缺失，转换不会中断，会记录 `LLM_CONFIG_MISSING` warning，并使用规则解析。

DashScope OpenAI 兼容模式示例：

```bash
export PAPERBRIDGE_OPENAI_API_KEY="your-api-key"
export PAPERBRIDGE_OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export PAPERBRIDGE_LLM_MODEL="qwen3.6-plus"
export PAPERBRIDGE_VLM_MODEL="qwen3.6-plus"

uv run paperbridge convert tests/fixtures/sample.pdf \
  --out /tmp/paperbridge-qwen-output \
  --use-vlm \
  --debug \
  --force \
  --json
```

## 输出结构

```text
output/
  paper.json
  paper.md
  paper.txt
  paper.docx
  summary.json
  assets/
    pages/
    figures/
    tables/
  debug/
    raw_blocks.json
    page_layouts.json
```

## 验证

生成示例 PDF：

```bash
uv run python tests/make_sample_pdf.py
```

运行测试：

```bash
uv run pytest
```

运行一次 smoke test：

```bash
uv run paperbridge convert tests/fixtures/sample.pdf --out /tmp/paperbridge-output --debug --force --json
```
