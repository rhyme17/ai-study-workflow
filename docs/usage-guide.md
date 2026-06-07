# AI Study Workflow 使用教程

适用场景：大学课程学习、期末复习、课件/PDF 消化、错题诊断、Anki 卡片生成。

当前 skill 位置：

```text
skills/ai-study-workflow
```

核心原则：先让学生作答，再让 AI 讲解、评分、生成卡片。不要一开始让 AI 直接总结整章。

## 1. 最快使用方式

在 Codex 里直接发：

```text
使用 ai-study-workflow，读取这个课件，先给我资料卡，然后让我选择新知识学习、期末复习或生成材料。不要先给答案。
```

如果你已经有文件，例如：

```text
使用 ai-study-workflow，读取 local-materials/course-files/course.pptx。我想快速提分，先走期末复习模式，先给 10 分钟闭卷诊断题，不要给答案。
```

你应该期待 AI 首轮只给：

- 资料卡：文件范围、页数/页码、文字是否可用、哪些页需要看图
- 模式选择：新知识学习 / 期末复习 / 生成材料
- 一个立即任务：诊断题或前置知识检查

不应该期待 AI 首轮输出几十页总结。

## 2. 三种模式怎么选

### A. 期末复习模式

适合：

- 课程已经学过
- 离考试近
- 想最快提分
- 不知道自己哪里薄弱

推荐提示：

```text
使用 ai-study-workflow，读取这个课件。我走期末复习模式。
请先给 8-10 道闭卷诊断题，覆盖核心概念、公式、场景应用。
不要给答案。等我回答后再评分、归因、安排下一步。
```

正确流程：

```text
资料检查 -> 10 分钟诊断 -> 你作答 -> AI 评分 -> 错因分类 -> 针对性补弱 -> 变式题 -> 卡片
```

评分时可以发：

```text
这是我的答案：...
请严格评分，分成 correct / missing / incorrect / likely cause / next drill / card candidates。
```

### B. 新知识学习模式

适合：

- 第一次学这个章节
- 课上没听懂
- 需要建立概念骨架

推荐提示：

```text
使用 ai-study-workflow，读取这个课件。我走新知识学习模式。
请先给章节骨架和 3-5 个前置检查问题。
不要直接长篇讲解，等我回答后再决定讲哪些。
```

正确流程：

```text
资料检查 -> 章节骨架 -> 前置检查 -> 你作答 -> AI 判断缺口 -> 小块讲解 -> 近迁移题 -> 远迁移题 -> 卡片
```

学习时不要说“直接帮我总结”。更好的说法是：

```text
我先尝试解释这个概念，你帮我找漏洞，不要直接替我说完整答案。
```

### C. 生成材料模式

适合：

- 想要知识地图
- 想要题库
- 想要 Anki/FSRS 卡片草稿
- 想把一份课件变成复习包

推荐提示：

```text
使用 ai-study-workflow，读取这个课件。先生成知识地图和题库草稿。
卡片只生成 front 草稿，不要生成完整 back，等我做题后再补。
```

## 3. PPTX 文件怎么处理

PPTX 优先用内置检查脚本：

```powershell
python .\skills\ai-study-workflow\scripts\inspect_pptx_source.py `
  .\local-materials\course-files\course.pptx `
  --markdown-out .\local-materials\test-runs\source-report.md `
  --json-out .\local-materials\test-runs\source-report.json `
  --text-out .\local-materials\test-runs\source-text.txt
```

检查报告会告诉你：

- 总共有多少页 slide
- notes 有多少
- 哪些页文字稀疏
- 哪些页图片/图示依赖高
- 哪些页需要视觉检查

如果报告里有 `image-heavy` 或 `graphic-content`，渲染关键页：

```powershell
python .\skills\ai-study-workflow\scripts\render_pptx_slides.py `
  .\local-materials\course-files\course.pptx `
  --from-report .\local-materials\test-runs\source-report.json `
  --flag image_heavy `
  --flag graphic_content `
  --max-slides 10 `
  --out-dir .\local-materials\test-runs\rendered-slides `
  --manifest-out .\local-materials\test-runs\rendered-slides\manifest.json
```

也可以手动渲染指定页：

```powershell
python .\skills\ai-study-workflow\scripts\render_pptx_slides.py `
  .\local-materials\course-files\course.pptx `
  --slides 3,28,72 `
  --out-dir .\local-materials\test-runs\rendered-slides
```

渲染后的 PNG 可以让 Codex 识图，用于解释网络拓扑、协议栈、封装图、排队图、公式图。

## 4. PDF 文件怎么处理

PDF 建议分三层处理：普通文本先用 MarkItDown 快速抽 Markdown，随后用内置脚本检查页级质量；公式、图表、复杂表格或扫描页再用 Docling 或页面渲染补强。

普通 PDF 先跑 MarkItDown：

```powershell
& "C:\Users\lenovo\.codex\tools\markitdown\Scripts\markitdown.exe" `
  .\local-materials\course-files\course.pdf `
  > .\local-materials\test-runs\pdf-markitdown.md
```

跑完后先看 `pdf-markitdown.md` 是否可读。如果出现大量乱码、`�`、表格全是 `?`、中文源文件几乎没有中文，或者公式/符号明显损坏，不要把它当作主要来源。

然后检查文字抽取质量：

```powershell
python .\skills\ai-study-workflow\scripts\inspect_pdf_source.py `
  .\local-materials\course-files\course.pdf `
  --markdown-out .\local-materials\test-runs\pdf-report.md `
  --json-out .\local-materials\test-runs\pdf-report.json `
  --text-out .\local-materials\test-runs\pdf-text.txt
```

如果 MarkItDown 输出为空、乱码、明显漏内容，或者 PDF 包含公式、图片、图表、复杂表格、扫描页，可以用 Docling 补充结构化解析。对于很大的课件导出 PDF 或图片很多的 PDF，不要默认整本跑 Docling；先用检查报告挑少量关键页，必要时把 PDF 复制到纯英文路径或拆分页段后再跑。

```powershell
$env:no_proxy = "127.0.0.1,localhost,127.0.0.0/8"
$env:NO_PROXY = $env:no_proxy
& "C:\Users\lenovo\.codex\tools\docling\Scripts\docling.exe" `
  .\local-materials\course-files\course.pdf `
  --to md `
  --image-export-mode referenced `
  --enrich-formula `
  --enrich-picture-description `
  --enrich-chart-extraction `
  --output .\local-materials\test-runs\docling-output
```

如果报告显示公式、符号、图片页有问题，继续渲染页面：

```powershell
python .\skills\ai-study-workflow\scripts\render_pdf_pages.py `
  .\local-materials\course-files\course.pdf `
  --from-report .\local-materials\test-runs\pdf-report.json `
  --flag private_use_symbols `
  --flag image_dependent `
  --max-pages 10 `
  --out-dir .\local-materials\test-runs\rendered-pages
```

PDF 的关键点：MarkItDown 和 Docling 都是抽取/结构化工具，不是高保真视觉复原。公式、特殊符号、图表、视觉推导不能只信文本抽取；被标记的页面要看渲染图或回到原 PDF 核对。

如果 Docling 报页数不一致、内存不足、OCR 失败或 Windows 临时文件占用，不要卡在转换上。直接使用 `pdf-report.md` / `pdf-text.txt` 建立章节地图，并渲染关键页让 Codex/GPT 识图。

如果 PDF 是 handout 格式，一页里有多张 slide，先渲染几页确认版式。之后 source tag 不要只写 `pdf-p5`，要写成 `pdf-p5-top-right`、`pdf-p5-slide-4-18` 这类能定位到具体小页/区域的标签。

## 5. 使用一份网络课程 PPTX 的推荐流程

这份课件已检查过：

- 89 slides
- 86 notes slides
- 109 media files
- 4 sparse slides
- 30 image-heavy slides
- 2 graphic-content slides

最快复习入口：

```text
使用 ai-study-workflow，基于 local-materials/course-files/course.pptx。
我走期末复习模式。请先给 10 道闭卷诊断题，覆盖：
protocol、network edge/core、packet switching、circuit switching、delay、traffic intensity、throughput、layering、encapsulation。
不要给答案。
```

最快新学入口：

```text
使用 ai-study-workflow，基于 local-materials/course-files/course.pptx。
我走新知识学习模式。请先给章节骨架和 5 个前置检查问题。
等我回答后，再讲第一个最关键模块。
```

图示页处理：

```text
请渲染并识别 slide 72，结合文字抽取解释 encapsulation 图。
把视觉来源标记为 visual-derived，并保留 slide-72 source tag。
```

## 6. 一次完整复习循环

1. 让 AI 检查资料。
2. 选择期末复习模式。
3. AI 给闭卷诊断题，不给答案。
4. 你作答。
5. AI 评分并分类错误。
6. AI 只讲你错的点。
7. AI 给一道近似题和一道变式题。
8. 你再答。
9. AI 把真实错误变成 Anki 卡片。
10. 第二天只复习错题卡和再测薄弱点。

推荐追问：

```text
基于我的错误，只生成 3 张最高价值 Anki 卡片，每张只考一个点，带 source tag。
```

## 7. 一次完整新知识循环

1. 让 AI 检查资料。
2. 选择新知识学习模式。
3. AI 给章节骨架和前置检查。
4. 你回答自己知道什么。
5. AI 判断缺口。
6. AI 讲一个小块。
7. 你用自己的话解释。
8. AI 找漏洞。
9. AI 给近迁移题。
10. 你答完后再看讲解。

推荐追问：

```text
我先用自己的话解释 packet switching。你只指出漏洞，并问我最多 3 个追问，不要直接给完整答案。
```

## 8. Anki CSV 怎么生成

准备一个 JSON 文件，例如：

```json
[
  {
    "front": "What happens when traffic intensity approaches 1?",
    "back": "Queueing delay grows rapidly; the system becomes unstable under sustained overload.",
    "deck": "Computer Networking",
    "tags": "chapter1 delay",
    "source": "slide-52"
  }
]
```

生成 CSV：

```powershell
python .\skills\ai-study-workflow\scripts\make_anki_csv.py `
  .\local-materials\test-runs\cards.json `
  --out .\local-materials\test-runs\cards.csv
```

卡片规则：

- 一张卡只考一个点
- 优先来自真实错误
- 每张卡带 source tag
- 不确定内容标记 `needs human check`

## 9. 质量检查清单

每次使用后检查：

- AI 有没有先让你回答？
- 有没有把答案藏到你回答之后？
- 有没有标记资料抽取缺陷？
- 图示/公式有没有渲染或标记 `needs human check`？
- 计划是不是围绕你的错误，而不是泛泛总结？
- 有没有明确下一步练习？
- 卡片是不是来自真实错误？

如果没有做到，直接纠正：

```text
请回到 ai-study-workflow 规则：先诊断，不要先给答案；只根据我的错误安排下一步。
```

## 10. 最推荐的默认提示

```text
使用 ai-study-workflow，读取我提供的课程文件。
先做资料卡，说明可用文本、需要看图的页、可能不可靠的地方。
然后给我三种选择：新知识学习、期末复习、生成材料。
如果我没有特别说明，默认选择期末复习，先给 10 分钟闭卷诊断题。
不要给答案，等我回答后再评分和安排下一步。
```
