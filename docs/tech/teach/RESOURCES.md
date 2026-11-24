# MinerU Teaching Resources

> Version baseline: MinerU 4.1.7 (repository `master`). Prefer the repository's own docs and source over external summaries.

## Knowledge

- [Internal doc: `docs/next/architecture.md`](../../next/architecture.md)
  The authoritative short description of current call relationships and ownership boundaries. Use for: DocVortex vs MinerU split, service responsibilities, local document-library chain.
- [Internal doc: `docs/next/code-map.md`](../../next/code-map.md)
  Module-to-responsibility map and the two main call chains. Use for: orienting a change to the right package.
- [Internal doc: `docs/next/tiers.md`](../../next/tiers.md)
  Tier/effort semantics, per-entry default selection, service tier ceilings, and fallback rules. Use for: any "which tier?" or "why did it choose this tier?" question.
- [Internal doc: `docs/next/workflows.md`](../../next/workflows.md)
  End-to-end workflows for stateless parsing, HTTP Tasks, Doclib, scan/watch, and rendering. Use for: entry-point behaviour and lifecycle.
- [Internal doc: `docs/next/config.md`](../../next/config.md)
  Two-phase configuration model, precedence, runtime KV keys, remote VLM, LLM-aided postprocess. Use for: configuration and deployment questions.
- [Internal doc: `docs/next/invariants.md`](../../next/invariants.md)
  Non-negotiable implementation invariants (privacy, ownership, protocol, locators). Use for: judging whether a proposed change is safe.
- [Internal doc: `docs/next/pitfalls.md`](../../next/pitfalls.md)
  Current 4.1 traps: per-entry default tiers, backend vs tier, compatibility boundary, error/cancel semantics. Use for: avoiding 3.x habits.
- [Internal doc: `docs/next/model-assets.md`](../../next/model-assets.md)
  Model repos, required files, GGUF main/mmproj, backend selection, offline runs. Use for: engine/weights/deployment questions.
- [Internal docs: `docs/next/cli/`](../../next/cli/)
  `mineru-kit api-server`, `vlm-server`, `router`, `models`, `mineru server`, `mineru parse/read`. Use for: exact options and lifecycle.
- [Internal docs: `docs/next/api/`](../../next/api/)
  Tasks endpoints, responses/errors, Router admin, health/models/tiers. Use for: protocol-level integrations.
- [Internal SDK docs: `docs/next/sdk/parser.md`](../../next/sdk/parser.md) and [`parse-result.md`](../../next/sdk/parse-result.md)
  Public SDK contract for `parse()` / `MinerUParser` / `ParseResult`. Use for: API-level questions and examples.
- [Source: `mineru/parser/`](../../../mineru/parser/)
  Input preparation, tier mapping, page ranges, local/remote parser facades. Use for: what happens before analysis.
- [Source: `mineru/backend/analyze.py`](../../../mineru/backend/analyze.py)
  The unified analysis facade and `ModelJson` construction. Use for: routing and metadata questions.
- [Source: `mineru/backend/analysis/pdf/`](../../../mineru/backend/analysis/pdf/)
  PDF window orchestration, layout, native text, OCR, formulas, tables, inline recognition. Use for: the core inference pipeline.
- [Source: `mineru/model/`](../../../mineru/model/)
  Model assets, runtime selection, device policy, VLM engines, local model lifecycle. Use for: engine and hardware questions.
- [Source: `mineru/render/`](../../../mineru/render/)
  Nine render targets and option contracts. Use for: output-format changes.
- [Source: `mineru/doclib/`](../../../mineru/doclib/)
  Stateful library: SQLite, ingest, queue, execution, content read, locators, background workers. Use for: caching, reading, and library services.
- [Source: `mineru/tasks/`](../../../mineru/tasks/) and [`mineru/kit/`](../../../mineru/kit/)
  HTTP task protocol, Router, file-parse wrapper, Gradio UI. Use for: service integration.
- [Project constraints: `CLAUDE.md`](../../../CLAUDE.md)
  Import rules, lazy loading, determinism, DocVortex boundary, lint/format policy. Use for: making changes that fit the codebase.
- [3.x course archive: `docs/tech/teach-old/`](../teach-old/)
  Previous 15-lesson course (MinerU 3.x). Use for: teaching structure, application scenarios, and finetune/evaluation/deployment framing. Do not use its APIs or engine names as 4.x facts.
- [User-facing README (Chinese)](../../../README_zh-CN.md)
  Tiers, model-engine matrix, install paths, agent guidance. Use for: product-level framing and tier trade-offs.
- [Official documentation](https://opendatalab.github.io/MinerU/)
  Published user docs (quick start, usage, reference, migration). Use for: stable public behaviour.
- [DocVortex repository](https://github.com/myhloli/docvortex)
  The shared document layer. Use for: native-format parsers, schema, deterministic postprocess, generic renderers. Do not read its private internals for MinerU product questions.
- [OmniDocBench](https://github.com/opendatalab/OmniDocBench)
  Standard document-parsing benchmark. Use for: general regression comparisons; not a substitute for your business target set.
- [vLLM OpenAI-compatible server](https://docs.vllm.ai/en/stable/serving/openai_compatible_server/)
  Serving and quantization options for remote VLM. Use for: deployment and quantized-model acceptance.
- [llama.cpp](https://github.com/ggml-org/llama.cpp)
  `convert_hf_to_gguf.py` and `llama-quantize` for GGUF main/mmproj. Use for: local llama.cpp deployment.
- [MinerU GitHub repository](https://github.com/opendatalab/MinerU)
  Issues, discussions, release notes. Use for: known bugs, migrations, and design context.

## Wisdom (Communities)

- [GitHub Discussions — opendatalab/MinerU](https://github.com/opendatalab/MinerU/discussions)
  High-signal venue for tier trade-offs, deployment questions, and quality comparisons. Use for: questions that need practitioner experience.
- [GitHub Issues — opendatalab/MinerU](https://github.com/opendatalab/MinerU/issues)
  Bug reports and reproduction cases. Search before filing; include version, hardware, tier, and logs.
- [Discord — MinerU](https://discord.gg/Tdedn9GTXq)
  Real-time community chat. Use for: quick troubleshooting and deployment experience. Ask before joining.
- [ModelScope community portal](https://mineru.net/community-portal/)
  Chinese-language community portal. Use for: model and deployment discussions in Chinese.

## Gaps

- No official deep-dive on the PDF processing-window orchestration or inline-formula VLM fallback; the source and `docs/next/tiers.md` are the authority.
- Router internals (worker discovery, leases) have no standalone doc; read `mineru/kit/router/`.
- No in-repo training or evaluation harness; lesson 16 provides a minimal A/B skeleton, but production metrics (TEDS, business field F1) need external tooling.
- DocVortex's internal implementation is out of scope until the public boundary is insufficient.
