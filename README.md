# AI Study Workflow

AI Study Workflow is a reusable Agent Skill for university learning and final-exam review. It turns course files into an active study loop:

```text
source inspection -> mode choice -> closed-book diagnostic -> feedback -> weak-point repair -> spaced-repetition cards
```

The project is designed for Codex, Claude Code, Gemini CLI, and other file-based agents.

## What It Does

- Inspects PPTX and PDF course material before generating study content.
- Marks sparse, visual, formula-heavy, or uncertain material as `needs human check`.
- Supports two main modes:
  - New knowledge learning: prerequisite check, concept skeleton, chunked tutoring, transfer tasks.
  - Exam review: closed-book diagnostic, grading, mistake taxonomy, targeted drills.
- Generates reusable prompts, study templates, and Anki CSV files.
- Renders PPTX slides or PDF pages to PNG for visual inspection when text extraction is incomplete.

## Repository Layout

```text
.
├── skills/ai-study-workflow/          # Canonical Agent Skill source
├── .codex/skills/ai-study-workflow/   # Codex project skill copy
├── .claude/skills/ai-study-workflow/  # Claude Code project skill copy
├── docs/
│   ├── usage-guide.md                 # End-user tutorial
│   ├── evaluations/                   # Workflow and UX test reports
│   └── research/                      # Original research workflow notes
├── examples/                          # Safe prompts and examples
├── scripts/                           # Repository maintenance scripts
└── local-materials/                   # Ignored local course files and generated outputs
```

`skills/ai-study-workflow` is the source of truth. The `.codex` and `.claude` copies exist so those tools can discover the skill from their native project-level locations.

## Quick Start

Use this prompt with an attached or local course file:

```text
Use ai-study-workflow. Read the course file first.
Start with a source card, then let me choose new learning, exam review, or material generation.
If I do not specify a mode, default to exam review and give me a 10-minute closed-book diagnostic.
Do not show answers until I respond.
```

For Chinese use:

```text
使用 ai-study-workflow，读取我提供的课程文件。
先做资料卡，说明可用文本、需要看图的页、可能不可靠的地方。
然后给我三种选择：新知识学习、期末复习、生成材料。
如果我没有特别说明，默认选择期末复习，先给 10 分钟闭卷诊断题。
不要给答案，等我回答后再评分和安排下一步。
```

## Install and Use

### Codex

This repository already includes:

```text
.codex/skills/ai-study-workflow/SKILL.md
```

Open the repository in Codex and ask to use `ai-study-workflow`.

### Claude Code

This repository already includes:

```text
.claude/skills/ai-study-workflow/SKILL.md
```

Open the repository in Claude Code and invoke:

```text
/ai-study-workflow
```

or ask naturally for AI-assisted final review or new knowledge learning.

### Gemini CLI and Other Agents

Use `AGENTS.md` or `GEMINI.md` as the project entry point, then load:

```text
skills/ai-study-workflow/SKILL.md
```

Generic agents that support the Agent Skills convention can use the canonical skill directory directly.

## Working With Course Files

Do not commit private course material. Put local PPTX/PDF files under:

```text
local-materials/course-files/
```

That directory is ignored by Git.

See [docs/usage-guide.md](docs/usage-guide.md) for full commands and examples.

## Validate the Skill Scripts

Use the bundled Python runtime if available, or any Python 3.10+ environment with the required packages installed.

```powershell
python -m py_compile `
  skills/ai-study-workflow/scripts/inspect_pdf_source.py `
  skills/ai-study-workflow/scripts/render_pdf_pages.py `
  skills/ai-study-workflow/scripts/inspect_pptx_source.py `
  skills/ai-study-workflow/scripts/render_pptx_slides.py `
  skills/ai-study-workflow/scripts/make_anki_csv.py
```

## Sync Adapter Copies

After editing the canonical skill under `skills/ai-study-workflow`, sync the Codex and Claude copies:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync-agent-skills.ps1
```

## Upload Notes

Before pushing to GitHub:

1. Check that `local-materials/` is ignored.
2. Do not commit original course PPTX/PDF files.
3. Do not commit rendered slide/page PNGs unless they are public and intentionally included.
4. Review generated study content for copyrighted or private course text.
