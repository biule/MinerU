# Learning record: 3.x archive gap analysis and course expansion

On 2026-11-24 the 3.x archive (`docs/tech/teach-old/`, 15 lessons) was compared with the 4.1.7 workspace (12 lessons). The archive's APIs and engine names are obsolete, but four teaching directions were worth importing:

1. **Stage-based curriculum** — foundation → practice → source/debug → extension → finetune → production. Adopted as `reference/study-plan.html` (8 stages, 3 target routes, per-lesson evidence standards).
2. **Application focus** — invoice parsing, batch pipeline, output field extraction, CSV summary. Adopted as lesson 14.
3. **Deep VLM/engine debugging** — call chain, engine selection, lifecycle, failure triage. Adopted as lesson 13; the archive's 3.x backend names were replaced with 4.x `tier` / `small backend` / `VLM engine`.
4. **Full finetune-to-production lifecycle** — the 4.1.7 course stopped at serving; added evaluation + quantization (lesson 16) and deployment/operations (lesson 17). The archive's small-image OCR bypass was re-verified against 4.x `AtomModelSingleton` and adopted as lesson 15.

Also added `reference/faq.html` for high-frequency phenomena, and corrected defects found during the comparison:

- Lesson 09 claimed public errors include `type/retryable/user_action`; `docs/next/api/responses.md` and `mineru/tasks/contracts.py` show only `code/message/param`. Fixed.
- Lesson 07 had nonsensical quiz options for the upload method (now `PUT`) and Tasks output formats (now `EPUB` as the unsupported one).
- Lessons 01/02/03/04/08/09/11/12 used translated or garbled quiz answers where exact identifiers matter; normalized to `flash/basic/standard/advanced`, `medium/high/xhigh`, `Content List`, `DocVortex`, `HTML`, error codes, etc.
- Lesson 12 had typos (`comm`, `rar`, `vfs`) and literal backticks; fixed.

**Status**: 17 lessons authored/cross-linked. All quizzes remain unattempted; no new competency evidence beyond LR-0001/LR-0002. The next session should collect evidence for lessons 13–17 (engine triage, batch output, small-image comparison, A/B report, deployment runbook) before writing a competency record.
