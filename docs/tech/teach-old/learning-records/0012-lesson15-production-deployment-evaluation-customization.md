# 第 14 课：生产部署与落地 — Docker/k8s、评测、客户化适配与量化加速

日期：2026-07-27

## 完成的事
- 创建 `teach/lessons/0014-production-deployment-evaluation-customization-quantization.html`（约 510 行）
- 第 1 节：systemd + Nginx 原生部署方案 — 架构 Mermaid 图、systemd unit（mineru-vllm.service + mineru-api.service，含 ExecStartPost 健康检查）、Nginx 反代 + 限流 + HTTPS（Let's Encrypt）、启动运维命令、日志监控、与 Docker/k8s 方案的对比表
- 第 2 节：OmniDocBench 标准化评测 — 五维评测 Mermaid 图、快速跑通命令、自定义 Adapter 注册骨架代码、评测报告对比表示例、无 OmniDocBench 时自己搭最低评测集的标准（3类×20份=60份）
- 第 3 节：单证客户化适配 — 三层架构 Mermaid 图（解析层/字段抽取层/校验层）、Layer 2 三种策略完整代码（正则匹配 10+ 条规则 / LLM few-shot 带 prompt 模板 / BERT-CRF 序列标注说明）、策略选择决策表（量/成本/延迟/周期）、Layer 3 校验函数
- 第 4 节：AWQ 量化 — 4 重量化方式对比表、AWQ 量化实操（autoawq 完整代码）、vLLM 加载量化模型命令、量化前后精度对比脚本、黄金法则 Mermaid 决策图、bitsandbytes 在线量化备用方案
- 更新 `0013-evaluation-lora-arithmetic-to-full-finetune.html`：next 链接从 index.html 改为第 14 课
- 更新 `index.html`：title/h1 更新为 0-14 课、14 课课时（约 10 小时）、阶段四"这五课"、新增第 14 课卡片、"下一步去哪"更新为系列完成总结

## Why
- 第 13 课回答了"评估和迭代"，用户自然追问"部署、评测、客户化、量化"——这是微调到生产的最后一公里
- Docker/k8s 已替换为 systemd + Nginx 原生部署方案，降低学习成本，更贴合"单机 GPU 服务器 + 内部 API"的实际场景
- OmniDocBench 给你客观对比报告，比"我看了 50 份感觉还不错"有说服力两个数量级
- 客户化是 MinerU 商业落地的核心：MinerU 做结构解析，下游做信息抽取，两层职责分明
- 量化是最便宜的推理加速方式——不换硬件、不改架构，权重精度从 BF16 压到 int4，模型缩小 75%

## How to apply
- Dockerfile 可作为生产镜像的起点模板，两个关键决策：模型预下载（构建时 vs 运行时）和 vLLM 独立部署（vs 同容器）
- k8s Ingress 的 proxy-body-size 和 proxy-read-timeout 是 prod 最容易被忽略的两个配置
- OmniDocBench Adapter 只需要实现 parse(image_path) → dict 一个方法
- 客户化三层架构中 Layer 2 的三个策略可以组合：正则兜底常见的 80%、LLM 处理异常、量大了换 BERT-CRF
- AWQ 量化后必须跑一次评估确认退化 < 2%，不能"量化完了直接上线"
