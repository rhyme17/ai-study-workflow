# Changelog

## v0.1.1

PDF ingestion quality update.

- Added stricter quality checks for MarkItDown PDF output.
- Documented fallback behavior for corrupted, visual, formula-heavy, scanned, and handout-style PDFs.
- Improved Windows UTF-8 console handling in the PDF inspector.
- Reduced false positives from benign private-use bullet glyphs in Chinese lecture PDFs.
- Added guidance for panel-level source tags when one PDF page contains multiple slide panels.
- Synced Codex and Claude Code skill copies with the canonical skill.

## v0.1.0

Initial public version of ai-study-workflow.

- Added reusable AI study workflow skill
- Added source inspection workflow for PDFs/PPTX
- Added closed-book diagnostic flow
- Added weak-point repair flow
- Added Anki CSV generation guidance
- Added examples and usage guide
