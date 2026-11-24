# 第 13 课：从微调走向生产 — 评估、叠加、增强与全参跃迁

日期：2026-07-27

## 完成的事
- 创建 `teach/lessons/0013-evaluation-lora-arithmetic-to-full-finetune.html`（约 490 行）
- 第 1 节：1000 份文档批量 A/B 评估 — 评估架构（Mermaid 图）、7 种指标速查表（CER/WER/Table Exact Match/TEDS/Formula Edit/Layout F1/Layout mAP）、Python 并行评估脚本骨架（ProcessPoolExecutor + scipy.stats.ttest_rel + Cohen's d）、统计检验解释、无 Ground Truth 时的四种替代方案（人工盲评/GPT-4 judge/启发式信号/下游任务）
- 第 2 节：LoRA 算术 — 权重合并公式和 Task Arithmetic 原理、三种叠加方式（PEFT add_weighted_adapter/LLaMA-Factory 联合训练/手动合并 safetensors）含完整代码、叠加可行性决策表、α 权重网格搜索脚本
- 第 3 节：训练数据增强 — albumentations 文档图片增强 pipeline（几何+像素+光照+分辨率+伪影）、Layout 增强的 bbox 同步变换约束（min_visibility=0.3）、Content 增强、合成字体渲染放量（5 字体 × 随机大小）、增强策略决策表（数据量 vs 增强倍数 vs 注意事项）
- 第 4 节：全参微调工程准备 — 硬件底线表、DeepSpeed ZeRO-3 完整 JSON 配置（带注释）、全参 vs LoRA 9 项配置差异表（含"为什么不同"解释）、数据量级与过拟合风险、WandB 监控六信号、Checkpoint 策略、决策清单 7 条
- 更新 `0012-finetuning-data-and-llama-factory.html`：next 链接从 index.html 改为第 13 课
- 更新 `index.html`：13 课课时、阶段四描述从"这三课"改为"这四课"、新增第 13 课卡片、候选下一课更新

## Why
- 第 12 课跑通了微调但缺少"跑完之后怎么办"——用户自然问出四个后续问题（A/B 评估 / LoRA 叠加 / 数据增强 / 全参微调）
- 批量评估是工业化微调的门槛：不量化效果就无法迭代
- LoRA 算术是多能力组合的杠杆——训练 3 个小 adapter 比训练一个大的更灵活
- 全参微调的工程准备清单可以拦住不切实际的期待——大多数人不需要但需要知道为什么不需要

## How to apply
- 评估脚本中的 ProcessPoolExecutor + paired t-test 模式可以直接用于任何模型对比
- LoRA add_weighted_adapter 的 α 扫描逻辑适用于任何多 adapter 场景
- albumentations BboxParams 是 Layout 增强的核心约束，忘记加会污染全部训练数据
- DeepSpeed ZeRO-3 配置可作为标准模板
- 第 13 课结尾埋了四个新种子问题（Docker/k8s / OmniDocBench / 客户化适配 / 量化），可接任一个
