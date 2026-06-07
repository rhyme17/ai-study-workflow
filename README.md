# AI Study Workflow

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/github/license/rhyme17/ai-study-workflow)
![Status](https://img.shields.io/badge/status-experimental-orange)

Turn lecture PDFs and PPTX files into closed-book diagnostics, targeted weak-point repair, and Anki cards.

把课件和 PDF 变成闭卷诊断、薄弱点补强和 Anki 卡片。

## Why This Exists

Most students ask AI to summarize lecture slides.
That feels productive, but it is still passive review.

AI Study Workflow is an agent skill that makes the student answer first.
It inspects course files, creates a closed-book diagnostic, waits for the student's answers,
grades strictly, repairs weak points, and turns real mistakes into spaced-repetition cards.

```text
source inspection -> closed-book diagnostic -> grading feedback -> weak-point repair -> Anki cards
```

It is not a generic "summarize my PPT" prompt.
The default flow is active recall: the agent asks questions first, withholds answers,
grades the student's attempt, and only then explains or generates cards.

## 30-Second Start

Attach a course PDF/PPTX and say:

```text
Use ai-study-workflow.
Inspect the source first.
Then give me a 10-minute closed-book diagnostic.
Do not reveal answers until I respond.
```

中文：

```text
使用 ai-study-workflow。先检查课程 PDF/PPTX，再给我 10 分钟闭卷诊断题。不要在我回答前公布答案。
```

## Who Is This For?

- Students reviewing lecture slides, PDFs, or course notes.
- People preparing for finals or closed-book exams.
- Users of Codex, Claude Code, Gemini CLI, or other file-based agents.
- Learners who want active recall instead of passive summaries.
- People who want Anki-ready cards after diagnosis and correction.

## Project Status

This is an experimental but usable workflow for AI-assisted studying.
It is designed for iterative use with real course materials and should be checked against
the original source when content is visual, formula-heavy, or ambiguous.

## Example Output

See:

- [Demo review session](examples/demo-review-session.md)
- [Anki output example](examples/anki-output-example.csv)
- [Reusable prompts](examples/prompts.md)

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
- back: When another link, sender/receiver limit, congestion,
  or protocol overhead becomes the bottleneck.
```

## What It Does

- Inspects PPTX and PDF course material before generating study content.
- Uses MarkItDown for fast first-pass PDF Markdown extraction when the output is readable.
- Uses Docling or rendered page images as fallback evidence for formula-heavy, visual, table-heavy, scanned, or incomplete PDF extraction.
- Marks sparse, visual, formula-heavy, conflicting, or uncertain material as `needs human check`.
- Starts review with closed-book diagnostics instead of summaries.
- Supports new knowledge learning with prerequisite checks and chunked tutoring.
- Generates targeted drills, mistake taxonomies, and Anki-ready CSV files.
- Renders PPTX slides or PDF pages to PNG when visual inspection is needed.

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

Generic agents that support the Agent Skills convention can use the canonical skill
directory directly.

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

`skills/ai-study-workflow` is the source of truth.
The `.codex` and `.claude` copies exist so those tools can discover the skill from
their native project-level locations.

## Working With Course Files

Put local PPTX/PDF files under:

```text
local-materials/course-files/
```

That directory is ignored by Git.
See [docs/usage-guide.md](docs/usage-guide.md) for full commands and examples.

For ordinary PDFs, the workflow can use MarkItDown as the first-pass extractor when its
output is readable, then run the bundled PDF inspector for page-level quality checks.
Formula-heavy, visual, table-heavy, scanned, corrupted, or incomplete extractions should
be checked with Docling and/or rendered page images before generating final explanations
or Anki card backs.

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

After editing the canonical skill under `skills/ai-study-workflow`, sync the Codex and
Claude copies:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync-agent-skills.ps1
```

## Version

Current prepared public version: `v0.1.1`.

See [CHANGELOG.md](CHANGELOG.md) for release notes and
[docs/repository-settings.md](docs/repository-settings.md) for recommended GitHub
metadata, topics, and social preview settings.

## Version History

- `v0.1.1`: Improves PDF ingestion quality checks, especially for Chinese course PDFs, handout-style slide exports, and visual/formula-heavy pages.
- `v0.1.0`: Initial public active-recall workflow with source inspection, closed-book diagnostics, weak-point repair, and Anki CSV guidance.

## License

MIT. See [LICENSE](LICENSE).
