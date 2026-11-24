# 第 9 课配套时序图：MinerU VLM 调用链

把下面的 mermaid 代码块复制到 [mermaid.live](https://mermaid.live) 即可在线渲染。第 9 课 HTML 内嵌了相同源码，CDN 可用时自动渲染。

## 完整异步调用链 + CUDA 报错冒泡

```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant CLI as "client.py:main"
    participant FAPI as "fast_api.py (子进程)"
    participant AIO as "aio_do_parse"
    participant APH as "_async_process_hybrid"
    participant HAA as "aio_doc_analyze"
    participant GMA as "_get_model_async"
    participant GM as "ModelSingleton.get_model"
    participant SLB as "set_lmdeploy_backend"

    U->>CLI: mineru -p demo.pdf -b hybrid
    CLI->>CLI: run_orchestrated_cli 起子进程
    CLI->>FAPI: POST /file-upload + /task-start
    FAPI->>AIO: run_parse_job → aio_do_parse
    Note over AIO: backend ≠ pipeline
    AIO->>APH: _async_process_hybrid
    APH->>HAA: aio_hybrid_doc_analyze
    HAA->>GMA: _get_model_async 首次加载
    GMA->>GM: asyncio.to_thread get_model
    GM->>SLB: set_lmdeploy_backend cuda
    SLB->>SLB: torch.cuda.is_available = False
    SLB-->>GM: raise ValueError CUDA is not available
    GM-->>GMA: 异常冒泡
    GMA-->>HAA: 异常冒泡
    HAA-->>APH: 异常冒泡
    APH-->>AIO: 异常冒泡
    AIO-->>FAPI: Async task failed
    FAPI-->>CLI: /task-status = failed
    CLI-->>U: 错误退出
```

## 同步链 vs 异步链分叉（mermaid flowchart）

```mermaid
flowchart LR
    A[client.py main] --> B[run_orchestrated_cli]
    B --> C[fast_api.py run_parse_job]
    C --> D{backend?}
    D -->|pipeline| E[do_parse 同步]
    E --> F[_process_pipeline]
    D -->|hybrid / vlm-*| G[aio_do_parse 异步]
    G --> H[_async_process_hybrid]
    H --> I[aio_hybrid_doc_analyze]
    I --> J[_get_model_async]
    J --> K[ModelSingleton.get_model]
    K --> L[set_lmdeploy_backend]
    L --> M{torch.cuda.is_available?}
    M -->|True| N[构建 lmdeploy engine]
    M -->|False| O[raise ValueError]
```

## 关键节点行号对照

| 节点 | 文件:行号 | 说明 |
|---|---|---|
| main | `mineru/cli/client.py:1185` | Click 入口 |
| run_orchestrated_cli | `mineru/cli/client.py:910` | 起子进程 + 提交任务 |
| run_parse_job | `mineru/cli/fast_api.py:822` | 子进程里执行任务 |
| do_parse（同步） | `mineru/cli/common.py:668` | pipeline 后端走这里 |
| aio_do_parse（异步） | `mineru/cli/common.py:766` | hybrid / vlm-* 走这里 |
| _async_process_hybrid | `mineru/cli/common.py:508` | hybrid 分支 |
| aio_doc_analyze | `mineru/backend/hybrid/hybrid_analyze.py:1116` | hybrid 主入口 |
| _get_model_async | `mineru/backend/vlm/vlm_analyze.py:265` | asyncio.to_thread 包裹 |
| get_model | `mineru/backend/vlm/vlm_analyze.py:199` | ModelSingleton 单例 |
| set_lmdeploy_backend | `mineru/backend/vlm/utils.py:60` | ★ CUDA 检查点（raise 在 `:66`） |

## 渲染说明

- **HTML 内嵌版**：第 9 课 HTML 通过 `cdn.jsdelivr.net/npm/mermaid@10` 加载 mermaid.js，打开 HTML 自动渲染。无网环境下不渲染，但 `<details>` 折叠块里有源码可看。
- **GitHub / VS Code**：直接把本文档的 mermaid 代码块复制过去，GitHub README 和 VS Code Markdown Preview 都原生支持 mermaid。
- **在线编辑**：粘贴到 [mermaid.live](https://mermaid.live) 可以实时调整样式、导出 SVG/PNG。
