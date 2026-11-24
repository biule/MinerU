# 第 12 课：微调数据构造 + LLaMA-Factory 实操

日期：2026-07-27

## 完成的事
- 创建 `teach/lessons/0012-finetuning-data-and-llama-factory.html`（约 440 行）
- 第 1 节补充了"权重"的前置知识：浮点数矩阵本质、BF16/FP32/int8/int4 精度对比、safetensors vs Pickle、模型文件组成（权重 + config.json + tokenizer + processor）、训练的三步循环（前向 → Loss → 反向）
- 第 2 节讲清微调 = 改权重，三种方式对比（全参 / LoRA / 冻结+分类头），LoRA 原理用公式和 Mermaid 图拆解
- 第 4-5 节分别覆盖 Step 1 Layout Detection 和 Step 2 Content Extraction 的数据构造：特殊 token 语法、27 种 block 类型、三种构造方法（人工标注 / MinerU 反向生成 / 合成数据）、Python 转换脚本骨架、数据量参考表
- 第 6 节完整 LLaMA-Factory 实操：环境搭建 → ShareGPT 格式转换 → dataset_info.json 注册 → YAML 配置详解 → 单卡/多卡/WebUI 三种启动方式 → export 合并 → 接回 MinerU 的两种方法
- 第 7 节经验与避坑：数据质量检查清单、训练策略建议表、6 个常见问题速查、显存预算参考表
- 更新 `0011-vlm-finetuning-and-wsl2-vllm.html`：next 链接从 index.html 改为第 12 课
- 更新 `index.html`：阶段四描述从"这两课"改为"这三课"，新增第 12 课卡片，更新使用建议

## Why
- 第 11 课回答了"能不能微调、用什么框架"，但用户问"具体怎么造数据、怎么跑通"时需要一份实操指南
- "权重"这个概念在 11 课中反复出现但未展开，理解它才能理解微调的本质
- LLaMA-Factory 的 ShareGPT 格式、dataset_info.json 注册、YAML 配置等步骤，没有一份完整的示例代码很难第一次就跑通

## How to apply
- 第 12 课结尾已埋三个种子问题（A/B 评估 / LoRA 算术 / 数据增强），下一课可接其中任何一个
- 新增第 13+ 课需同步更新 index.html 的阶段四卡片
- Step 1 / Step 2 的数据格式不同，不要混着训——这条教训在 HTML 中用 highlight-amber 强调
