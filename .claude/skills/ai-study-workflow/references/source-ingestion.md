# Source Ingestion

Use this before building a study workflow from PDFs, slides, lecture notes, screenshots, OCR output, or mixed materials.

## Quick Source Pass

1. Identify source type: PDF, slides, notes, textbook, problem set, past paper, rubric, or mixed.
2. Check scope: page count, chapter/topic range, course name, and whether the file is one chapter or the whole exam scope.
3. Check extraction quality:
   - usable text
   - sparse pages
   - missing formulas or symbols
   - broken ordering
   - image-only pages
   - slide notes or speaker notes
4. Build a compact source map: page range -> topic.
5. Mark uncertain evidence as `needs human check`.

## PDF Extraction Strategy

For PDF files, separate text extraction from reliability checking:

1. Use MarkItDown first for ordinary text PDFs when available. It usually gives a fast, clean Markdown draft for LLM reading.
2. Check the MarkItDown output for mojibake, replacement characters (`�`), missing expected CJK/text content, broken formulas/tables, and obvious scope loss.
3. Run the bundled PDF inspector for page-level quality flags before creating a learning or review plan.
4. Use Docling when MarkItDown output is empty, visibly incomplete, or the file is formula-heavy, image-heavy, chart-heavy, table-heavy, scanned, or layout-sensitive.
5. Render flagged pages when formulas, diagrams, charts, private-use symbols, or image-dependent pages affect the explanation, diagnostic questions, or Anki backs.

For ordinary PDFs, run:

```powershell
& "C:\Users\lenovo\.codex\tools\markitdown\Scripts\markitdown.exe" course.pdf > source-markitdown.md
```

Use `source-markitdown.md` as a first-pass reading source only when the output appears complete, readable, and consistent with the PDF's scope. Do not rely on it alone for formulas, diagrams, charts, or source-sensitive answers.

Quick rejection signals:

- high replacement-character count (`�`) or visible mojibake
- very low expected Chinese/CJK text in a Chinese source
- table rows filled with `?` or missing labels
- formulas converted to private-use glyphs or unreadable symbols
- output length that is implausibly small for the page count

For slide-export or handout-style PDFs, render a few sample pages early. A single PDF page may contain multiple slide panels, so source tags should include both the PDF page and the visible panel or region, for example `pdf-p5-top-right` or `pdf-p5-slide-4-18`, not just `pdf-p5`.

## PDF Inspector

Run the bundled inspector before creating a learning or review plan:

```bash
python scripts/inspect_pdf_source.py course.pdf --markdown-out source-report.md --json-out source-report.json --text-out source-text.txt
```

Use the Markdown report to brief the user and the JSON report for exact page lists. Use the text output for page tags, topic mapping, and question generation, but do not treat it as complete when the report flags sparse pages, private-use symbols, or image-dependent pages.

The inspector reports:

- page count
- empty text pages
- sparse text pages
- private-use or suspect symbol pages
- benign private-use bullet glyphs are ignored when they look like list markers
- image-dependent sparse pages
- Poppler command availability
- per-page snippets and extracted text

## Docling Fallback

Use Docling when the PDF likely needs structure-aware extraction:

- formulas or mathematical notation
- images, figures, diagrams, or charts that carry meaning
- complex tables
- scanned or image-only pages
- layout-sensitive material
- empty or incomplete MarkItDown output

Recommended command:

```powershell
$env:no_proxy = "127.0.0.1,localhost,127.0.0.0/8"
$env:NO_PROXY = $env:no_proxy
& "C:\Users\lenovo\.codex\tools\docling\Scripts\docling.exe" course.pdf --to md --image-export-mode referenced --enrich-formula --enrich-picture-description --enrich-chart-extraction --output docling-output
```

The `no_proxy` override avoids a Windows-local `httpx` parsing issue caused by bare IPv6 localhost entries such as `::1`.

Use Docling's Markdown and referenced images as supplemental evidence. If the command is slow, retry with fewer enrichment flags before falling back to the normal PDF inspector plus rendered pages.

For large slide-export PDFs or image-heavy course decks:

- Do not run Docling over the whole file as the default fallback.
- Prefer copying the PDF to an ASCII-only local path before running Docling if the original path contains non-ASCII characters.
- Prefer running Docling on a split page range or small set of critical pages after the inspector identifies them.
- If Docling reports page-count, memory, OCR, or temporary-file cleanup errors, treat it as unavailable for that source and continue with inspector text plus rendered page images.

If `pdftoppm` is unavailable, state that visual rendering was not performed. For diagram-heavy or formula-heavy pages, keep `needs human check` until visual inspection or user confirmation.

## PDF Renderer

After inspection, render pages that need visual checks:

```bash
python scripts/render_pdf_pages.py course.pdf --from-report source-report.json --flag private_use_symbols --flag image_dependent --max-pages 10 --out-dir rendered-pages --manifest-out rendered-pages/manifest.json
```

Manual page selection is also supported:

```bash
python scripts/render_pdf_pages.py course.pdf --pages 1,28,41-43 --out-dir rendered-pages
```

Rendering uses PyMuPDF when available and falls back to Poppler `pdftoppm`. If neither backend is available, install PyMuPDF with:

```bash
python -m pip install PyMuPDF
```

Use rendered PNGs for visual model review of formulas, diagrams, tables, and pages whose extracted text is empty or sparse. Keep visual conclusions tied to page numbers and source tags.

After rendering, inspect the PNGs with the available image/vision capability before using the page for final explanations. For example, view a rendered page, extract the visible formula or diagram meaning, then merge that visual note with the text extraction report.

## PPTX Inspector

For PowerPoint files, prefer the bundled inspector before creating a learning or review plan:

```bash
python scripts/inspect_pptx_source.py course.pptx --markdown-out source-report.md --json-out source-report.json --text-out source-text.txt
```

The inspector reports:

- slide count
- notes slide count
- media file count
- sparse text slides
- image-heavy slides
- graphic-content slides
- notes-important slides
- per-slide snippets, notes snippets, and topic guesses

Use the text output for topic mapping and question generation, but do not treat it as complete when the report flags image-heavy or graphic-content slides.

When `notes_important` is flagged, read the notes snippet before deciding the topic's priority. Notes often contain instructor emphasis, narration, or clarifications that are not visible on the slide.

## PPTX Renderer

After inspection, render slides that need visual checks:

```bash
python scripts/render_pptx_slides.py course.pptx --from-report source-report.json --flag image_heavy --flag graphic_content --max-slides 10 --out-dir rendered-slides --manifest-out rendered-slides/manifest.json
```

Manual slide selection is also supported:

```bash
python scripts/render_pptx_slides.py course.pptx --slides 3,10-12,48 --out-dir rendered-slides
```

Rendering uses PowerPoint COM on Windows when available and falls back to LibreOffice-to-PDF plus PyMuPDF. If no rendering backend succeeds, keep image-heavy and graphic-content slides as `needs human check`.

After rendering, inspect the PNGs with the available image/vision capability before using diagrams, flow charts, screenshots, packet paths, protocol stacks, or formula layouts in final explanations. Label visual-derived notes as `visual-derived` and keep slide numbers attached.

## Reliability Rules

- Do not treat extracted text as complete when formulas, diagrams, tables, or symbols may be missing.
- Do not treat MarkItDown or Docling output as high-fidelity visual reconstruction.
- Prefer MarkItDown for ordinary text extraction, Docling for complex extraction, and rendered pages for visual verification.
- Reject text extraction that is readable only as mojibake, even if the command exits successfully.
- For large image-heavy PDFs, render and visually inspect critical pages before attempting broad OCR/Docling conversion.
- For handout PDFs where one PDF page contains multiple slides, keep panel-level source tags for visual-derived explanations and cards.
- Do not invent professor priorities from slide count alone.
- If two pages or examples appear to conflict, preserve both and mark `needs human check`.
- If a page has sparse text, say that visual inspection or user confirmation may be needed.
- If a slide is image-heavy or graphic-heavy, render it or mark it `needs human check`.
- If slides contain notes, consider notes part of the source; do not ignore them when building topic maps.
- Source tags should be specific enough to verify later: `pdf-p38-p41`, `lecture-3`, `assignment-2-q4`.
- For formula-heavy PDFs, do not finalize formulas or Anki card backs from pages flagged with private-use symbols until checked.

## Study Workflow Output

Every source-based workflow should include:

- source scope used
- quality caveat if extraction is incomplete
- source map or topic map
- human-check list for unclear scope, conflicting examples, or missing formulas

For first-turn interactive use, keep the output shorter:

- source card
- mode chooser
- for review, one answer-free diagnostic; for first-time learning, one small learning block plus a light check

## Interaction Rule

When generating diagnostic questions or practice tasks from source material:

1. Show questions first.
2. Ask the student to answer.
3. Withhold answers, worked solutions, and final card backs until the answer or an explicit request for solutions.
