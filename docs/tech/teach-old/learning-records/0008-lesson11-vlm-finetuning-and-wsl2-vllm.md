# 第 11 课学习记录

日期：2026-07-27

## 学习目标
- 弄清 MinerU 用的 VLM 模型身份（Qwen2-VL 骨架 + MinerU2.5-Pro-2605-1.2B 权重）
- 判断模型是否可微调，需要准备哪些数据和环境
- 理解 Windows 上 LMDeploy 被选中的真相（vLLM 不支持 Windows 原生）
- 在 Windows 11 上用 WSL2 跑通 vLLM 的完整步骤

## 覆盖范围
- 模型识别：`Qwen2VLForConditionalGeneration` + `opendatalab/MinerU2.5-Pro-2605-1.2B`
- 微调可行性分层分析（权重层/架构层/流程层/配置层）
- 两步推理的数据结构（Layout 检测 + 内容抽取各自的 prompt 与输出格式）
- 训练框架选型对比（LLaMA-Factory / Unsloth / ms-swift / Qwen 官方 / HF Trainer）
- 引擎选择源码追读（`engine_utils.py` 三平台分流逻辑）
- LMDeploy turbomind vs vLLM 在 Windows/Linux 上的性能差异
- WSL2 + vLLM 搭建完整流程（驱动、conda、PyTorch CUDA、模型下载、服务启动）
- `.wslconfig` 资源限制 + 常见坑速查

## 产出文件
- `teach/lessons/0011-vlm-finetuning-and-wsl2-vllm.html` — 第 11 课课件

## 关键认知
- MinerU 是纯推理框架，仓库内无训练脚本，微调需自行搭 pipeline
- MinerU 自定义了 special tokens（`<|box_start|>` 等），改 prompt 格式时 tokenizer 要同步扩展
- vLLM 在 pyproject.toml 中明确标注 `sys_platform == "linux"`，Windows 原生不支持
- LMDeploy 在 Windows 被强制 turbomind 后端，性能落后 Linux pytorch 后端 20-40%
- WSL2 GPU passthrough 通过 Windows N 卡驱动直接提供，不需在 WSL 内装驱动

## 待办
- 评估是否需要补充一节专门讲微调数据构造（标注 budget、弱监督方案）
- 用户如果决定走 WSL2 路线，下一课可以聚焦 LLaMA-Factory 实操
- 跨页表格合并 / 长 PDF 在 WSL2 上跑 vLLM 的实际性能基准（待用户实测）