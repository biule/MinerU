# 第 13 课：魔搭 SWIFT 微调实战

用户上完了第 13 课《魔搭 SWIFT 微调实战 — 从零到部署》，掌握了用魔搭社区 SWIFT 框架对 MinerU VLM 进行 LoRA 微调的完整流程。本课紧接第 12 课 LLaMA-Factory，提供第二个微调框架选项。

## 关键知识点
- SWIFT 与 LLaMA-Factory 的定位差异：SWIFT 是 Qwen/魔搭生态的"亲儿子"，互补而非替代
- 数据格式兼容：LLaMA-Factory ShareGPT JSON 和 SWIFT messages JSONL 字段名一致，只需 JSON 数组 → JSONL
- CLI 一条命令跑通：`swift sft` 覆盖全流程，Python API 用于自定义 loss 等进阶需求
- 训练后必须 merge_lora 再部署：生产用 mineru-vllm-server 而非 swift deploy
- SWIFT 独有功能：多轮对话训练、自定义 token-loss 加权、一键推送到魔搭 Hub

## 下一步建议
- 实际动手：在 WSL2/Linux 中装好 ms-swift，用现有训练数据跑通一次
- 数据迁移：把 LLaMA-Factory 格式的数据转为 JSONL 验证兼容性
- 魔搭 Hub：注册账号并尝试推送/拉取微调模型
- 进阶探索：多轮对话联合训练 Layout + Content（实验性）
