# Mission: Understand MinerU 4.x end-to-end to extend it

## Why
You maintain a fork of MinerU (`biule/MinerU`) and need to change its parsing pipeline, tier policy, model backends, and services with confidence — not just run it. Architecture knowledge is the prerequisite for shipping a custom capability without breaking existing behavior.

## Success looks like
- Trace any input file from CLI/SDK/API to `MiddleJson`, naming every decision point and module.
- Explain and choose among `flash/basic/standard/advanced`, including model engines and hardware constraints.
- Locate the exact seam for a change: PDF stage, model backend, renderer, Doclib endpoint, or service.
- Explain the VLM runtime: engine selection, cache key, remote `http-client`, lifecycle, and no-fallback semantics.
- Build a batch pipeline that chooses tiers, parses, extracts fields, isolates failures, and packages assets.
- Deploy and debug the stateless API, Doclib, Router, and VLM service from source-level knowledge.
- Prove a finetune or quantized model is better with a fixed A/B protocol, per-type metrics, and a rollback plan.
- Read a failing parse log and identify which stage, window, engine, or model produced it.

## Constraints
- Windows 11; conda environment `mineru` (Python 3.12); CPU-first, optional GPU.
- Chinese explanations preferred; source-level accuracy over marketing summaries.
- Learns by reading code, diagrams, and printable references.
- GitHub access is intermittent through a local proxy; lessons must not depend on live fetching.
- `docs/tech/teach-old/` is a 3.x-era archive: useful for teaching structure and application scenarios, not a factual source for 4.x APIs.

## Out of scope
- Training-framework internals and large-scale distributed training (serving and evaluating finetunes is in scope).
- DocVortex internals beyond its public boundary (for now).
- Cloud SaaS billing and operations.
