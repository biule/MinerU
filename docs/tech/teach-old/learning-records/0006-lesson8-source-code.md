# 第 8 课：深入源码与二次开发

用户上完了第 8 课《深入源码与二次开发》，掌握了 MinerU 源码结构和二次开发的基本能力。

## 关键知识点
- 完整的源码目录地图：cli层 → backend引擎层 → model模型层 → data数据层 → utils工具层
- 从 CLI 到输出的六节点调用链：client.py → common.py → pipeline_analyze.py → model_init.py → pipeline_middle_json_mkcontent.py → data_reader_writer.py
- 四个常用修改场景：改默认引擎、新增输出格式、调整 OCR 语言、修改处理窗口
- 调试三板斧：DEBUG 日志、中间 JSON 隔离定位、最小可复现案例
- 代码贡献流程：Fork → Clone → Branch → Code → Test → Commit → PR
- PEP 8 核心规则速查

## 学习进度
八节课系列完结。用户已从零基础覆盖了 MinerU 的完整学习路径：概念→架构→配置→实战→JSON→API→流水线→源码。

## 下一步建议
- 在实际项目中应用所学知识
- 阅读 `mineru/utils/enum_class.py` 中的所有枚举定义
- 在 GitHub Issues 中找 "good first issue" 标签的任务尝试贡献
- 阅读 `mineru/model/utils/pytorchocr/` 理解 PP-OCRv6 底层实现
