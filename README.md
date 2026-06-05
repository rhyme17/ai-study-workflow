# AI Study Workflow

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/github/license/rhyme17/ai-study-workflow)
![Status](https://img.shields.io/badge/status-experimental-orange)

Turn lecture slides and PDFs into active-recall study sessions: diagnostic quiz first, weak-point repair second, Anki cards last.

把课件/PDF 变成一套主动回忆复习流程：先闭卷诊断，再定位薄弱点，最后生成 Anki 卡片。

## Why This Exists

Most students ask AI to summarize lecture slides. That feels productive, but it is still passive review.

AI Study Workflow is an agent skill that makes the student answer first. It inspects course files, creates a closed-book diagnostic, waits for the student's answers, grades strictly, repairs weak points, and turns real mistakes into spaced-repetition cards.

```text
source inspection -> mode choice -> closed-book diagnostic -> grading -> weak-point repair -> Anki cards
```

## Who Is This For?

- Students who use AI to review lecture slides or PDFs.
- People preparing for finals, quizzes, retakes, or certification exams.
- Learners who want active recall instead of passive summaries.
- Users of Codex, Claude Code, Gemini CLI, or other file-based agents.
- Anyone building reusable agent skills for study workflows.

## Demo

**Input**

```text
Use ai-study-workflow. Read this lecture PPTX first.
I want fast exam review. Start with a 10-minute closed-book diagnostic.
Do not show answers until I respond.
```

**First response**

```text
Source card
- Scope: networking chapter, 89 slides
- Usable text: good
- Visual checks: 30 diagram-heavy slides need review before final explanations
- Caveat: optional appendix slides need exam-scope confirmation

Mode
- Defaulting to exam review because you asked for fast score improvement.

Closed-book diagnostic
1. What is a protocol?
2. What is the difference between the network edge and the network core?
3. Why does packet switching create queueing delay?
4. What does L/R represent in store-and-forward transmission?
...

Stop here. Send your answers before I grade or explain.
```

**After the student answers**

```text
correct:
- You correctly identified packet switching as shared-resource transmission.

missing:
- You did not mention syntax, semantics, and timing in the protocol definition.

incorrect:
- You treated throughput and bandwidth as always identical.

likely cause:
- Concept contrast gap: bandwidth vs achieved throughput.

next drill:
- Solve one path-throughput problem with three bottleneck links.

card candidates:
- source: slide-56
- front: When is throughput lower than a link's bandwidth?
- back: When another link, sender/receiver limit, congestion, or protocol overhead becomes the bottleneck.
```

See [examples/demo-review-session.md](examples/demo-review-session.md) for a complete example and [examples/anki-output-example.csv](examples/anki-output-example.csv) for sample card output.

## What It Does

- Inspects PPTX and PDF course material before generating study content.
- Marks sparse, visual, formula-heavy, conflicting, or uncertain material as `needs human check`.
- Starts review with closed-book diagnostics instead of summaries.
- Supports new knowledge learning with prerequisite checks and chunked tutoring.
- Generates targeted drills, mistake taxonomies, and Anki-ready CSV files.
- Renders PPTX slides or PDF pages to PNG when visual inspection is needed.

## Quick Start

Use this prompt with an attached or local course file:

```text
Use ai-study-workflow. Read the course file first.
Start with a source card, then let me choose new learning, exam review, or material generation.
If I do not specify a mode, default to exam review and give me a 10-minute closed-book diagnostic.
Do not show answers until I respond.
```

中文提示词：

```text
使用 ai-study-workflow，读取我提供的课程文件。
先做资料卡，说明可用文本、需要看图的页、可能不可靠的地方。
然后给我三种选择：新知识学习、期末复习、生成材料。
如果我没有特别说明，默认选择期末复习，先给 10 分钟闭卷诊断题。
不要给答案，等我回答后再评分和安排下一步。
```

## Install and Use

### Codex

This repository includes a project-level Codex skill:

```text
.codex/skills/ai-study-workflow/SKILL.md
```

Open the repository in Codex and ask to use `ai-study-workflow`.

### Claude Code

This repository includes a project-level Claude Code skill:

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
├── examples/                          # Demo sessions and safe prompts
├── assets/                            # Social preview and public project assets
├── scripts/                           # Repository maintenance scripts
└── local-materials/                   # Ignored local course files and generated outputs
```

`skills/ai-study-workflow` is the source of truth. The `.codex` and `.claude` copies exist so those tools can discover the skill from their native project-level locations.

## Working With Course Files

Put local PPTX/PDF files under:

```text
local-materials/course-files/
```

That directory is ignored by Git. See [docs/usage-guide.md](docs/usage-guide.md) for full commands and examples.

## Validate the Skill Scripts

Use any Python 3.10+ environment with the required packages installed:

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

## License

MIT. See [LICENSE](LICENSE).
