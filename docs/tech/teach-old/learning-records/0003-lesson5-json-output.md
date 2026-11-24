# 第 5 课：JSON 输出详解

用户上完了第 5 课《JSON 输出详解 — 结构化数据后处理》，了解了 MinerU JSON 输出的层次结构、三种格式的差异以及如何用 Python 程序化提取信息。

## 关键知识点
- JSON 输出的五层结构：根对象 → 页面 → 块 → 行 → 片段
- 三种 JSON 格式：middle_json（最完整）、content_list（平铺后处理）、content_list_v2（精细语义）
- 核心块类型：text、title、table、image、equation、code、list、header/footer
- bbox 归一化坐标：页面宽高映射为 [0, 1000]
- 用 Python 提取标题、表格和低置信度片段的方法
- 单证解析场景的 JSON 应用思路（发票字段提取、合同条款索引、报表数据入库）

## 学习进度
已完成第 1-5 课，覆盖了 MinerU 的基础概念、架构、配置、实战解析和 JSON 输出。

## 下一步建议
- 第 6 课：Python API 调用 — 从命令行到代码（用户需要实际用 API 拿到 JSON 输出）
- 第 7 课：高级配置与调优
