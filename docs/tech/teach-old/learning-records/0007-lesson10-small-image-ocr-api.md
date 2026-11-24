# 第 10 课学习记录

日期：2026-07-23

## 学习目标
- 理解 pipeline Layout 模型对小图的致命缺陷
- 掌握绕过 Layout 的 PaddleOCR 直调方案
- 在 FastAPI 中搭建生产可用的 /image_ocr REST API

## 覆盖范围
- MinerU 模型体系（PDF-Extract-Kit-1.0 的 7 个子模型）
- PytorchPaddleOCR 类直调（det + rec，跳过 Layout）
- fast_api.py 新增接口开发（Pydantic 模型、端点注册、Swagger 参数声明）
- base64 编解码的边界处理（data: 前缀剥离、自动 padding、长度 mod 4 校验）
- 图片预处理（短边放大、透明通道铺白底、PIL→numpy BGR）
- 并发批处理（asyncio.create_task）
- OCR 引擎单例缓存
- 生产部署方案（Wheel、Cython 编译、Nginx 反代）

## 产出文件
- mineru/cli/fast_api.py — 新增 /image_ocr/json 和 /image_ocr/upload 两个端点
- tests/unittest/test_imgbase64.py — pipeline + raw OCR 测试用例
- teach/lessons/0010-small-image-ocr-api.html — 第 10 课课件

## 待办
- 考虑是否需要专门的小图 OCR 微服务（独立于 mineru 主服务）
- 评估 Cython 编译 fast_api.py 的实际效果
