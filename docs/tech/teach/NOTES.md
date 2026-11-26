# Teaching Notes

## User preferences

- **Language**: Chinese explanations; keep technical identifiers and source paths in English.
- **Depth**: source-level accuracy. Prefer reading real code over marketing or blog summaries.
- **Format**: step-by-step; detailed flowcharts; rigorous comments on code snippets.
- **Reference style**: printable, Tufte-like HTML; cheat sheets should be reusable across sessions.
- **Location**: teaching workspace lives under `docs/tech/teach/` so it stays alongside the project's other engineering docs and does not pollute the repository root.

## Working environment

- Windows 11, Git Bash.
- Conda environment `mineru` (Python 3.12.16), MinerU 4.1.7 installed editable from this repository.
- GPU optional; CPU-first assumptions for lessons.
- GitHub network is intermittent through a local proxy. Lessons must work fully offline (no CDN dependencies, no live fetches required).
- Markdown documents (`MISSION.md`, `RESOURCES.md`, `NOTES.md`, learning records) are rendered to styled HTML with `python docs/tech/teach/build_md_html.py`; edit the `.md` source, then rerun the script.

## Teaching approach

- Start from the mission: be able to extend the fork safely.
- Use the repository's own `docs/next/` and source as the primary sources.
- One tightly-scoped lesson at a time; retrieval practice (quizzes) before moving on.
- Reference documents carry the compressed, printable knowledge; lessons carry the skill.
- Record genuine understanding in `learning-records/`, not mere coverage.
- Course shape: mainline 01–09 → model runtime 13 → application 14–15 → finetune 10–12 + acceptance 16 → operations 17. Use `reference/study-plan.html` for routes and evidence standards.

## Session log

- 2026-11-07: Workspace created. Initial course starts with tracing a PDF and choosing a tier.
- 2026-11-24: Expanded the course to 17 lessons. Added model runtime/VLM engine (13), batch pipeline and field extraction (14), small-image OCR extension (15), finetune evaluation and quantization (16), deployment and operations (17), plus `reference/study-plan.html` and `reference/faq.html`. Fixed error-schema and quiz defects found during the review. All quizzes remain unattempted; no new competency evidence yet.
