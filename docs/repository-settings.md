# Recommended Repository Settings

These settings help the project communicate its value clearly on GitHub.

## Description

Active-recall AI study workflow for course PDFs/PPTX, final review, diagnostics, weak-point repair, and Anki cards.

## Topics

Comma-separated:

```text
ai-study, active-recall, spaced-repetition, anki, exam-review, university, agent-skills, codex, claude-code, gemini-cli, pdf, pptx
```

One per line:

```text
ai-study
active-recall
spaced-repetition
anki
exam-review
university
agent-skills
codex
claude-code
gemini-cli
pdf
pptx
```

## Website

```text
https://github.com/rhyme17/ai-study-workflow#readme
```

## Social Preview

Use a simple cover image with this message:

```text
AI Study Workflow
PDF/PPTX → Diagnostic → Weak-Point Repair → Anki
```

Suggested asset in this repository:

```text
assets/social-preview.png
```

## Release

Recommended latest release: `v0.1.1`.

Title:

```text
v0.1.1 - PDF ingestion quality checks
```

## Release Notes

```text
PDF ingestion quality update.

- Added stricter quality checks for MarkItDown PDF output.
- Documented fallback behavior for corrupted, visual, formula-heavy, scanned, and handout-style PDFs.
- Improved Windows UTF-8 console handling in the PDF inspector.
- Reduced false positives from benign private-use bullet glyphs in Chinese lecture PDFs.
- Added guidance for panel-level source tags when one PDF page contains multiple slide panels.
- Synced Codex and Claude Code skill copies with the canonical skill.
```
