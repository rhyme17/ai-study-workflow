# AGENTS.md

This project packages an AI-assisted study workflow as a reusable Agent Skill.

## Primary Skill

Use the canonical skill when the user asks about learning, final review, course files, diagnostics, Anki cards, or study workflows:

```text
skills/ai-study-workflow/SKILL.md
```

Codex and Claude Code also have native project-level copies:

```text
.codex/skills/ai-study-workflow/SKILL.md
.claude/skills/ai-study-workflow/SKILL.md
```

## Core Behavior

- Inspect source material before generating study content.
- Prefer active recall over summaries.
- Ask the student to answer before revealing solutions.
- Mark sparse, visual, formula-heavy, conflicting, or uncertain material as `needs human check`.
- Use source tags for generated questions, explanations, and cards.
- Do not treat AI output as a final answer for graded work.

## Modes

- Review mode: use for exams, finals, weak-point diagnosis, mock tests, and score improvement.
- Learning mode: use for first-pass understanding, prerequisite checks, chunked tutoring, and transfer tasks.
- Material generation: use for topic maps, question banks, and Anki drafts.

## Local Material Policy

Private course files and generated renderings belong under `local-materials/`, which is ignored by Git. Do not upload original PPTX/PDF course files unless the user explicitly confirms they are public and allowed.

## Verification

Before reporting changes complete, run the narrowest useful checks, usually:

```powershell
python -m py_compile skills/ai-study-workflow/scripts/*.py
git status --short
```

If this directory is not a Git repository, report that clearly.
