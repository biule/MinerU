# Windows 开发环境准备：Miniconda + uv

> 归档日期: 2026-11-07
> 适用版本: MinerU 4.1.7 / Python 3.12 / Windows 11
> 定位: 工程环境记录。本文描述的 conda 环境用于**替代** `CLAUDE.md` 中的 `.venv`，源码仍为 editable 安装。

## 1. 目标与结论

`CLAUDE.md` 规定的环境流程是 `uv venv .venv` + `uv pip install -e ".[dev,test]"`。本机改用 conda 承载解释器与依赖隔离，uv 仍负责依赖解析和安装，二者不冲突。

最终产物:

| 项 | 值 |
| --- | --- |
| Miniconda | conda 26.9.4（`Anaconda.Miniconda3` py314_26.9.4-0） |
| 安装路径 | `C:\Users\Administrator\miniconda3` |
| 环境名 | `mineru` |
| 环境路径 | `C:\Users\Administrator\miniconda3\envs\mineru` |
| Python | 3.12.16（conda-forge） |
| uv | 0.13.6（`envs\mineru\Library\bin\uv.exe`） |
| mineru | 4.1.7（editable，指向 `C:\pro\src\mineru`） |
| docvortex | 0.6.20 |

Python 版本选择依据: `pyproject.toml` 要求 `>=3.11,<3.15`（4.0.12 时下限为 3.10），CI 覆盖 3.11–3.13，文档构建使用 3.12。选 3.12 兼容面最稳。

## 2. 安装 Miniconda

使用 winget 安装官方安装包:

```bash
winget install -e --id Anaconda.Miniconda3 --silent \
  --accept-package-agreements --accept-source-agreements
```

安装完成后 `conda init` 会自动处理 **cmd**（注册表 `Command Processor\AutoRun`）和 **Windows PowerShell**（`Documents\WindowsPowerShell\profile.ps1`），新开窗口即可使用。

## 3. 创建环境（绕开 Anaconda 默认源的 ToS）

Miniconda 默认频道 `repo.anaconda.com` 要求先接受 Anaconda 服务条款，非交互环境会直接报 `CondaToSNonInteractiveError`。本项目环境统一使用 **conda-forge**，不接触 Anaconda 默认频道:

```bash
conda create -n mineru python=3.12 -c conda-forge --override-channels -y
```

要点:
- `-c conda-forge --override-channels` 是必须的，否则 conda 仍会尝试默认源并触发 ToS 检查。
- 后续针对该环境的 `conda install` 同样带上这两个参数。
- 如果确实需要使用 Anaconda 默认源，需显式执行 `conda tos accept --override-channels --channel <url>`；商用场景需自行评估 Anaconda 的授权要求。

## 4. 安装 uv 到环境内

```bash
conda install -n mineru -c conda-forge --override-channels uv -y
```

注意: conda-forge 的 uv 安装在 `envs\mineru\Library\bin\uv.exe`，**不在** `Scripts\`。调用时建议使用绝对路径，避免依赖激活后的 PATH。

## 5. 安装项目依赖

```bash
UV="$USERPROFILE/miniconda3/envs/mineru/Library/bin/uv.exe"
PY="C:/Users/Administrator/miniconda3/envs/mineru/python.exe"

"$UV" pip install --python "$PY" \
  --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
  -e ".[dev,test]"
```

说明:
- `--python "$PY"` 显式指定目标解释器，无需先 `conda activate`。
- `-e` 为 editable 安装，修改源码即时生效，与 `CLAUDE.md` 的流程一致。
- extras 按 `CLAUDE.md` 取 `dev,test`；`torch` 在 Windows 上属于可选后端，不在这一步安装（见 §8）。
- 本机访问 PyPI 官方索引会 15s 超时，因此使用清华镜像。该参数仅对单次命令生效，未修改全局配置。

## 6. 验证

```bash
ENV="$USERPROFILE/miniconda3/envs/mineru"

"$ENV/python.exe" -c "import mineru, docvortex; from mineru.version import __version__; print(__version__)"
"$ENV/Scripts/mineru.exe" --version
"$ENV/Library/bin/uv.exe" pip check --python "$ENV/python.exe"
```

预期:

```
MinerU version: 4.1.7
Python version: 3.12.16
All installed packages are compatible
```

## 7. 日常使用

```bash
conda activate mineru

mineru --version
python -m pytest tests/unittest
uv pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <包名>
```

- **cmd / PowerShell**: 新窗口直接 `conda activate mineru`。
- **Git Bash**: `conda init` 不处理 Git Bash，需要手动在 `~/.bashrc` 加入:
  ```bash
  eval "$("$HOME/miniconda3/Scripts/conda.exe" shell.bash hook)"
  ```
  或在每次会话前手动执行该行。
- 当前 `auto_activate_base=True`（每次启动自动进入 base）。如需关闭:
  ```bash
  conda config --set auto_activate_base false
  ```

## 8. 代码更新后的环境同步

`git pull` 之后若 `pyproject.toml` 的依赖约束变化，需要按新规格重新同步环境（editable 安装的 mineru 版本号也会随之更新）:

```bash
git pull --ff-only origin master

"$USERPROFILE/miniconda3/envs/mineru/Library/bin/uv.exe" pip install \
  --python "C:/Users/Administrator/miniconda3/envs/mineru/python.exe" \
  --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
  -e ".[dev,test]"
```

实例（4.0.12 → 4.1.7）: 该区间把 `docvortex` 约束从 `>=0.5.16,<1` 改为 `>=0.6.13,<0.7`，并新增 `onnx>=1.19,<2`、Windows amd64 改用 `onnxruntime-directml`。重新同步后实际变更:

```
- docvortex==0.6.4
+ docvortex==0.6.20
- mineru==4.0.12
+ mineru==4.1.7
- mineru-vl-utils==2.0.7
+ mineru-vl-utils==2.0.8
+ onnx==1.23.2
```

可选后端（本地 pipeline 模型需要时）:

```bash
"$UV" pip install --python "$PY" --index-url https://pypi.tuna.tsinghua.edu.cn/simple -e ".[torch]"
```

## 9. 已知问题

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `CondaToSNonInteractiveError` | 默认频道未接受 Anaconda ToS | 使用 `-c conda-forge --override-channels` |
| `uv pip install` 长时间无输出 | PyPI 官方索引在本机超时 | 加 `--index-url https://pypi.tuna.tsinghua.edu.cn/simple` |
| `Scripts/uv.exe` 不存在 | conda 包把 uv 放在 `Library/bin` | 使用 `envs/mineru/Library/bin/uv.exe` |
| Git Bash 中 `conda: command not found` | `conda init` 不写 `.bashrc` | 手动追加 `shell.bash hook` 行 |
| `mineru.__version__` 不存在 | 版本号定义在 `mineru.version` | 使用 `from mineru.version import __version__` |
| conda 环境与 `.venv` 并存 | 两者独立 | 二者选一；本机使用 conda 环境 `mineru` |
