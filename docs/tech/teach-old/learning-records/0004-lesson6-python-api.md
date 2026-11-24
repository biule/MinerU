# 第 6 课：Python API 调用

用户上完了第 6 课《Python API 调用 — 从命令行到代码》，了解了如何用 Python 代码调用 MinerU 引擎进行程序化文档解析。

## 关键知识点
- CLI 与 Python API 的使用边界：CLI 适合临时测试，Python API 适合自动化流水线
- 核心五步工作流：读取文件(read_fn) → 准备目录(prepare_env) → 解析文档(doc_analyze_streaming) → 生成输出(union_make) → 写入文件(DataWriter)
- 回调函数模式：on_doc_ready 在文档解析完成时自动调用，支持边解析边输出
- MakeMode 四种输出：MM_MD(完整MD)、NLP_MD(纯文字)、CONTENT_LIST(结构化JSON)、CONTENT_LIST_V2(细粒度JSON)
- FileBasedDataWriter：文件写入抽象层，支持本地文件和 S3 云存储
- 批量处理：三个列表(pdf_bytes / image_writer / lang) 长度必须相等
- 三个引擎的 API 入口：pipeline 用 doc_analyze_streaming，hybrid/vlm 用 doc_analyze

## 学习进度
已完成第 1-6 课，覆盖了 MinerU 的基础概念、架构、配置、实战解析、JSON 输出和 Python API。

## 下一步建议
- 第 7 课：搭建单证解析流水线（将 CLI 和 API 知识整合为完整的数据处理流水线）
- 第 8 课：深入源码与二次开发
