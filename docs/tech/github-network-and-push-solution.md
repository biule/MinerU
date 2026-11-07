# GitHub 拉取与推送完整方案：受限网络下的 MinerU 仓库工作流

> 归档日期：2026-11-07
> 适用环境：Windows 11 + Git for Windows 2.54 + 本地混合代理（HTTP/SOCKS 7892）
> 定位：工程操作记录 + 原理讲解。记录「直连被阻断 → 分层诊断 → 镜像克隆 → 远端拓扑拆分 → PAT 认证 → 凭据持久化」的完整链路，可迁移到其他 GitHub 仓库。
> 约定：本文不包含任何真实 Token / 密码。示例一律使用占位符 `$GITHUB_TOKEN`。

---

## 0. 速查（TL;DR）

| 环节 | 本次遇到的现象 | 采用的方案 |
| --- | --- | --- |
| 代码获取 | `git clone https://github.com/...` 直连 TLS 握手失败 | 通过 `https://gh-proxy.com/https://github.com/...` 镜像克隆 |
| 远端拓扑 | 镜像只适合读，不适合写 | `origin` = 原始 GitHub；`mirror` = 加速镜像 |
| 推送认证 | ① 缓存账号 `EvanQuCN` 无仓库写权限（403）<br>② 账号密码认证被 GitHub 拒绝 | 使用 Personal Access Token（PAT） |
| 凭据持久化 | 不能把 Token 明文写进 `.git/config` | Git Credential Manager → Windows 凭据管理器（DPAPI 加密） |
| 网络链路 | 系统代理 `127.0.0.1:7892` 间歇性拒绝连接 | 仓库级 `http.https://github.com.proxy` + 重试策略 |
| 本地提交 | 存在未跟踪的 `docs/tech/` 文档 | 精确 `git add <path>` 后提交并推送 |

四条核心结论：

1. **Git 不会自动读取 Windows 的「系统代理」注册表设置**，必须显式配置 `http.proxy`（或设置 `HTTPS_PROXY` 环境变量）才会走代理。
2. DNS 返回 `198.18.x.x` 是代理软件 **TUN + fake-IP** 接管的典型标志；这类地址没有真实主机，代理核心一旦故障，连接会直接失败。
3. GitHub 自 **2021-08-13** 起不再接受账号密码进行 Git 传输层认证，HTTPS 推送必须使用 PAT / OAuth / SSH。
4. `403 Permission to <repo> denied to <user>` 与 `403 Password authentication is not supported` 是两种完全不同的错误：前者是权限问题，后者是认证方式问题。

---

## 1. 技术概述

### 1.1 目标

在「GitHub 直连被阻断、本地代理不稳定」的 Windows 机器上，完成以下闭环：

1. 拉取 `https://github.com/biule/MinerU.git` 的完整历史（非浅克隆）；
2. 保留后续与原始仓库同步的能力；
3. 具备向该仓库提交并推送的能力，且凭据不落明文；
4. 网络路径可解释、可复现、可切换。

### 1.2 四层约束模型

这类问题不能笼统归结为「网不好」，需要按层拆解。每一层都有独立的判断依据与独立的对策：

| 层次 | 约束 / 故障 | 本次观测证据 | 对策 |
| --- | --- | --- | --- |
| ① 名称解析层 | DNS 被代理软件接管，返回 fake-IP | `github.com → 198.18.0.11` | 需要代理核心在线；或改用可解析的镜像域名 |
| ② 传输层 | 直连 GitHub 的 443 被阻断；代理 CONNECT 间歇失败 | 真实 GitHub IP `:443` 全部 TCP 失败；代理端口时通时不通 | 走代理或镜像；增加重试；检查代理进程 |
| ③ Git 协议层 | 镜像站通常只支持读 | `git ls-remote` 经 `gh-proxy.com` 成功 | 读写分离：`origin` 负责推送，`mirror` 负责拉取 |
| ④ 认证与凭据层 | 密码认证被禁用；缓存凭据属于错误账号 | `Password authentication is not supported`；`denied to EvanQuCN` | 使用 PAT；用 GCM 加密存储；必要时清理旧凭据 |

### 1.3 最终状态快照

| 项 | 值 |
| --- | --- |
| 工作目录 | `C:\pro\src\customMineru` |
| 仓库 | fork of `opendatalab/MinerU`（`biule/MinerU`） |
| 默认分支 | `master` |
| 克隆时 HEAD | `8cd08422`（`chore: sync recent releases in issue templates`，2026-11-04） |
| 包体积 / 对象数 | 185.10 MiB / 51,088 |
| 本次新增提交 | `ab3ef54d`（`docs: add Windows Miniconda + uv environment setup notes`） |
| `origin`（读写） | `https://github.com/biule/MinerU.git` |
| `mirror`（只读加速） | `https://gh-proxy.com/https://github.com/biule/MinerU.git` |
| 仓库级代理 | `http.https://github.com.proxy = http://127.0.0.1:7892` |
| 凭据存储 | Git Credential Manager 2.7.3 → Windows 凭据管理器 |
| Git 版本 | 2.54.0.windows.1 |

---

## 2. 总体流程图

```mermaid
flowchart TB
    Start(["开始：需要获取 biule/MinerU"]) --> A["阶段 A：环境勘察<br/>目录 / git 配置 / 端口 / 进程"]
    A --> B{"直连 github.com 可用？"}
    B -- "是" --> CloneDirect["git clone 原始地址"]
    B -- "否" --> C["阶段 B：分层诊断<br/>DNS → TCP → TLS → HTTP 代理"]
    C --> D{"代理 CONNECT 可用且稳定？"}
    D -- "是" --> CloneProxy["git clone 经代理"]
    D -- "否 / 不稳定" --> E{"镜像站 gh-proxy.com 可用？"}
    E -- "是" --> CloneMirror["git clone 经镜像"]
    E -- "否" --> Retry["更换网络 / 修复代理后重试"]
    Retry --> C
    CloneDirect --> F["阶段 D：远端拓扑<br/>origin=GitHub, mirror=镜像"]
    CloneProxy --> F
    CloneMirror --> F
    F --> G["阶段 E：认证与推送"]
    G --> H{"认证结果"}
    H -- "403 无写权限" --> H1["确认账号 / 添加 Collaborator"]
    H -- "密码认证被拒" --> H2["改用 PAT（repo / Contents 写权限）"]
    H -- "成功" --> I["阶段 F：凭据持久化<br/>GCM approve + 校验"]
    H1 --> G
    H2 --> G
    I --> J["阶段 G：提交文档并验证远端 ref"]
    J --> End(["完成"])
```

---

## 3. 分阶段详解

### 3.1 阶段 A：环境勘察

先确认「我们在哪、手里有什么」，避免在错误前提上排障。

#### 3.1.1 工作目录与 Git 状态

```bash
ls -la "C:/pro/src/customMineru"
git -C "C:/pro/src/customMineru" status
```

本次结果：目录为空，且不是 Git 仓库（`fatal: not a git repository`）。因此不存在「覆盖已有文件」的风险，可以直接在目标目录落地仓库内容。

#### 3.1.2 现有 Git 配置

```bash
# 查看与代理 / URL 重写相关的全局配置
git config --global --get-regexp 'proxy|url\.'
```

本次结果：

```text
url.https://github.com/.insteadof git@github.com:
```

含义：把 SSH 形式 `git@github.com:...` 自动改写为 HTTPS。**该规则不影响 HTTPS URL 本身**，但说明这台机器曾经为「SSH 不可用」做过适配。

#### 3.1.3 代理端口探测

先按常见端口盲测：

```bash
# -x http://127.0.0.1:<port>：把该端口当作 HTTP 代理访问目标
# --max-time 5：单次最多 5 秒，避免盲测卡死
# -o /dev/null -w "%{http_code}"：只关心状态码
for p in 7890 7897 1080 10809 8080 8888 33210; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 \
    -x "http://127.0.0.1:$p" https://github.com 2>/dev/null)
  echo "port $p -> $code"
done
```

本次结果全部为 `000`（不可用）。**盲测失败不代表没有代理**，只是端口不在常见列表里。随后通过监听端口反查：

```bash
# 列出所有 LISTENING 状态的本地端口及所属 PID
netstat -ano | grep -i listen
```

发现 `127.0.0.1:7892`。再确认进程归属：

```powershell
# PowerShell：按 PID 查进程名与可执行文件路径
Get-Process -Id 4028 | Select-Object Id, ProcessName, Path | Format-List
```

结果：

| 项 | 值 |
| --- | --- |
| 监听端口 | `127.0.0.1:7892` |
| 进程 | `ziyoumaoCore.exe`（PID 4028） |
| 关联进程 | `ziyoumao`（GUI）、`ziyoumaoHelperService`（服务） |
| 同时存在 | Cisco AnyConnect（`vpnagent` / `vpnui`），其虚拟网卡处于 Disconnected |

#### 3.1.4 系统代理设置

```bash
# Windows 系统代理（IE 设置）保存在当前用户注册表中
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" \
  | grep -iE "ProxyEnable|ProxyServer|AutoConfigURL"
```

结果：`ProxyEnable = 1`、`ProxyServer = 127.0.0.1:7892`。

**关键认知**：系统代理是给浏览器等使用 WinINET/WinHTTP 的程序准备的；Git for Windows 基于 libcurl，**不会**自动读取该注册表项。因此即使系统代理可用，Git 仍需显式配置。

#### 3.1.5 网络接口与路由

```powershell
Get-NetAdapter | Select-Object Name, InterfaceDescription, Status
Get-NetRoute -DestinationPrefix '0.0.0.0/0'
```

结果：Realtek 有线网卡 Up，默认路由 `192.168.0.1`，metric 0；AnyConnect 虚拟网卡 Disconnected。说明底层物理链路正常，问题不在「没网」，而在「出网路径」。

---

### 3.2 阶段 B：网络分层诊断

#### 3.2.1 DNS：识别 fake-IP

```bash
nslookup github.com
```

本次结果：

```text
Server:  UnKnown
Address:  fdfe:dcba:9876::2

Name:    github.com
Address:  198.18.0.11
```

判读要点：

- `198.18.0.0/15` 是 RFC 2544 保留的基准测试网段，真实公网服务不会使用。
- 代理客户端的 **TUN + fake-IP** 模式会劫持 DNS，对「需要代理的域名」返回一个假地址（从保留网段中分配），并把该假地址的流量路由进 TUN，由代理核心按映射表还原域名后转发。
- 因此：假地址本身不可直连。**代理核心在线时可用；核心退出或节点不可用时，连接表现为超时或拒绝**。

作为对照，`ghfast.top` 解析到了真实 IP `107.175.190.204`，说明 DNS 整体并未失效，只是对不同域名采用了不同策略。

#### 3.2.2 TCP：区分「网络全断」与「目标被阻断」

```powershell
# PowerShell：仅做 TCP 层连通性测试，不涉及 TLS
Test-NetConnection -ComputerName 223.5.5.5 -Port 443 -InformationLevel Quiet
Test-NetConnection -ComputerName 140.82.113.4 -Port 443 -InformationLevel Quiet
```

本次结果：

| 目标 | 结果 | 判读 |
| --- | --- | --- |
| `223.5.5.5:443` | `True` | 本机到公网某些目标的 443 可达 |
| `140.82.113.4:443`（GitHub） | `False` | GitHub 直连被阻断 |
| `140.82.112.3:443`（GitHub） | `False` | 同上 |
| `20.205.243.166:443`（GitHub） | `False` | 同上 |

结论：**不是全局断网，而是目标级别的阻断**。这决定了后续策略必须是「换路径（代理/镜像）」，而不是「修本机网络」。

#### 3.2.3 TLS：确认握手失败点

```bash
# -v：输出握手细节；输出重定向到文件/管道以免干扰
curl -v --max-time 20 https://github.com -o /dev/null
```

本次关键输出：

```text
* Host github.com:443 was resolved.
* IPv4: 198.18.0.11
*   Trying 198.18.0.11:443...
* schannel: failed to receive handshake, SSL/TLS connection failed
curl: (35) schannel: failed to receive handshake, SSL/TLS connection failed
```

Git 的两种 TLS 后端表现：

| 后端 | 配置 | 报错 |
| --- | --- | --- |
| Schannel（默认，Windows 原生） | 默认 | `schannel: failed to receive handshake, SSL/TLS connection failed` |
| OpenSSL（Git 自带） | `-c http.sslBackend=openssl` | `TLS connect error: error:0A000126:SSL routines::unexpected eof while reading` |

偶发成功时，OpenSSL 的详细日志显示 `SSL certificate verified via OpenSSL.`，说明**证书链没有问题**，失败发生在网络路径/代理隧道，而不是证书校验。

#### 3.2.4 HTTP 代理行为与不稳定性

```bash
# 纯 HTTP 请求：代理可以直接转发
curl -s -o /dev/null -w "%{http_code}\n" --max-time 15 \
  -x http://127.0.0.1:7892 http://cp.cloudflare.com/generate_204
```

结果：`204`，说明代理进程的 **HTTP 转发能力正常**。

```bash
# HTTPS 请求：客户端会先向代理发 CONNECT，建立隧穿
curl -sv --max-time 20 -x http://127.0.0.1:7892 https://github.com -o /dev/null
```

结果在 `200`、`000`、`Connection refused` 之间反复。`netstat` 显示端口仍在 LISTENING，但 `Test-NetConnection -Port 7892` 返回 `False` —— 典型的**代理核心处于异常/过载状态**：监听套接字存在，但不接受新连接或无法完成上游建连。

这解释了两次看似矛盾的观测：

1. 同一时刻 `ls-remote github.com` 可能成功；
2. 紧接的下一次重试全部失败。

**结论：代理链路不可作为唯一路径，必须准备无代理的镜像路径。**

#### 3.2.5 镜像站探测

```bash
# 逐个测试候选镜像的根路径可达性
for u in https://ghproxy.net https://gh-proxy.com https://kkgithub.com \
         https://bgithub.xyz https://hub.gitmirror.com https://gitclone.com; do
  printf "%s -> " "$u"
  curl -s -o /dev/null -w "%{http_code}\n" --max-time 12 "$u"
done
```

本次结果：

| 镜像 | HTTP 状态 | 判读 |
| --- | --- | --- |
| `gh-proxy.com` | 200 | 可用 |
| `ghproxy.net` | 200（随后 `ls-remote` 连接失败） | 可达但不稳定 |
| `gitclone.com` | 200（随后 `ls-remote` 连接失败） | 可达但不稳定 |
| `kkgithub.com` | 000 | 不可用 |
| `bgithub.xyz` | 000 | 不可用 |
| `hub.gitmirror.com` | 000 | 不可用 |

进一步用 Git 协议验证（比 HTTP 首页更可靠）：

```bash
# 镜像 URL 规则：镜像域名 + "/" + 原始完整 URL
git ls-remote --heads \
  "https://gh-proxy.com/https://github.com/biule/MinerU.git"
```

本次结果：

```text
8cd08422055858f55a64dff79f942318b51b96cc    refs/heads/master
```

**这是决定性证据**：镜像不仅能访问，还能正确转发 Git smart HTTP 协议。

#### 3.2.6 诊断决策树

```mermaid
flowchart TD
    S(["症状：git clone 失败"]) --> D1["nslookup 目标域名"]
    D1 --> D2{"返回 198.18.x.x？"}
    D2 -- "是" --> F1["TUN + fake-IP 接管<br/>流量依赖代理核心"]
    D2 -- "否" --> D3{"返回真实公网 IP？"}
    D3 -- "否" --> X1["DNS 故障<br/>检查解析器 / hosts"]
    D3 -- "是" --> T1
    F1 --> T1["TCP 443 连通性测试"]
    T1 --> T2{"TCP 可达？"}
    T2 -- "否" --> P1["目标被阻断 / 代理链路故障"]
    T2 -- "是" --> T3["TLS / HTTP 握手测试"]
    T3 --> T4{"握手成功？"}
    T4 -- "否" --> P2["中间设备干扰 / 代理隧道异常"]
    T4 -- "是" --> G1["Git 协议层测试<br/>git ls-remote"]
    G1 --> G2{"成功？"}
    G2 -- "是" --> OK["原路径可用"]
    G2 -- "否" --> P3["认证 / 路径 / 代理配置问题"]
    P1 --> M1["探测本地代理端口"]
    M1 --> M2{"代理 CONNECT 可用？"}
    M2 -- "是" --> OK2["配置 http.proxy 后重试"]
    M2 -- "否 / 不稳定" --> M3["探测镜像站<br/>git ls-remote 验证"]
    M3 --> M4{"镜像可用？"}
    M4 -- "是" --> OK3["通过镜像克隆"]
    M4 -- "否" --> X2["更换网络环境 / 修复代理"]
```

---

### 3.3 阶段 C：镜像克隆

#### 3.3.1 镜像 URL 的构造规则

```text
https://gh-proxy.com/https://github.com/<owner>/<repo>.git
└──────┬──────────┘└──────────────────────────────────┘
   镜像域名               原始仓库完整 URL（协议 + 路径，含 .git）
```

Git 后续的 `info/refs?service=git-upload-pack`、`git-upload-pack` 等请求都会以同样前缀转发到上游。因此镜像必须支持 **Git smart HTTP 协议**，而不仅仅是静态文件下载。

#### 3.3.2 为什么克隆到临时目录再移动

直接 `git clone ... .` 失败会留下不完整状态（半成品 `.git`、部分工作区）。Git 对非空目录执行 clone 会直接拒绝，因此「失败后原地重试」是不可行的；而清空目标目录又涉及不可逆删除。

本次采用的做法：

```bash
# 每次尝试使用一个全新的、唯一的临时目录，失败后无需删除任何东西
git clone --progress \
  "https://gh-proxy.com/https://github.com/biule/MinerU.git" \
  /c/pro/src/customMineru-clone-gh

# 仅在成功（.git 存在且 HEAD 可解析）后，才发布到工作目录
# dotglob 让 * 匹配隐藏文件（包括 .git）
shopt -s dotglob
mv /c/pro/src/customMineru-clone-gh/* /c/pro/src/customMineru/
rmdir /c/pro/src/customMineru-clone-gh   # 仅当目录为空时成功
```

这样做的性质：

- **失败隔离**：每次尝试互不影响，不会因部分对象残留导致下一次失败。
- **发布近似原子**：同一卷内的 `mv` 本质是目录项重命名，速度快；只有全部内容就位后才对用户可见。
- **无破坏性删除**：不执行 `rm -rf`，降低误删风险。

#### 3.3.3 克隆重试状态机

```mermaid
stateDiagram-v2
    [*] --> NewAttempt: 初始化 attempt = 1
    NewAttempt --> Cloning: 新建唯一临时目录
    Cloning --> Verifying: git clone 结束
    Verifying --> RetryWait: 失败（未产生可解析 HEAD）
    RetryWait --> NewAttempt: sleep 3s；attempt + 1
    Verifying --> Publish: 成功（.git 存在且 HEAD 可解析）
    Publish --> [*]: mv 到工作目录并校验
```

本次实际过程：

- 先尝试「本地代理 + 重试」：15 次全部失败（代理拒绝连接）。
- 改用镜像后：一次成功，约 3–4 分钟内下载 222 MB 工作区（其中 pack 185.10 MiB）。

#### 3.3.4 克隆后的完整性校验

```bash
# 1) 确认 HEAD 指向正确提交
git -C /c/pro/src/customMineru log -1 --oneline

# 2) 校验对象库完整性（--no-progress 让输出只保留错误）
git -C /c/pro/src/customMineru fsck --no-progress

# 3) 查看打包体积与对象数量（-vH 人类可读单位）
git -C /c/pro/src/customMineru count-objects -vH

# 4) 确认工作区干净、分支跟踪关系正确
git -C /c/pro/src/customMineru status -sb
```

本次结果：

```text
8cd08422 chore: sync recent releases in issue templates
in-pack: 51088
size-pack: 185.10 MiB
## master...origin/master
```

`git fsck` 无输出即无错误。至此，代码获取闭环完成。

---

### 3.4 阶段 D：远端拓扑设计

#### 3.4.1 克隆带来的默认状态

直接克隆镜像 URL 后，`origin` 会是镜像地址，推送也会指向镜像：

```text
origin  https://gh-proxy.com/https://github.com/biule/MinerU.git (fetch)
origin  https://gh-proxy.com/https://github.com/biule/MinerU.git (push)
```

问题在于：**镜像站通常只支持读**（反向代理/缓存的定位是加速下载）。若保持该状态，后续 `git push` 会失败，且语义上也不正确。

#### 3.4.2 读写分离的两种设计

方案一（本次采用）：两个远端，职责明确。

```bash
# origin 恢复为真实的 GitHub 地址：负责推送（以及代理可用时的拉取）
git remote set-url origin https://github.com/biule/MinerU.git

# mirror 专门用于走镜像拉取
git remote add mirror "https://gh-proxy.com/https://github.com/biule/MinerU.git"
```

方案二：单远端 + 分离 push URL。

```bash
# fetch 继续走镜像，push 走原始地址
git remote set-url origin "https://gh-proxy.com/https://github.com/biule/MinerU.git"
git remote set-url --push origin https://github.com/biule/MinerU.git
```

| 维度 | 方案一（两远端） | 方案二（pushurl） |
| --- | --- | --- |
| 语义清晰度 | 高：`origin` 就是标准远端 | 中：`origin` 的 fetch/push 指向不同主机 |
| 日常命令 | `git fetch mirror` / `git push origin` | `git fetch origin` / `git push origin` |
| 工具兼容性 | 好 | 少数工具对 pushurl 支持不完整 |
| 切换成本 | 低 | 低 |

本次选择方案一，便于排障时一眼看出「这次操作走的是镜像还是原站」。

#### 3.4.3 拓扑示意

```mermaid
flowchart LR
    W["本地仓库<br/>C:/pro/src/customMineru"] -->|"fetch / pull<br/>（加速）"| M["mirror<br/>gh-proxy.com"]
    W -->|"push<br/>（需代理 + PAT）"| O["origin<br/>github.com/biule/MinerU"]
    M -.->|"反向代理转发"| O
```

图中虚线表明：镜像只是原站的代理，不产生独立的历史；因此经镜像拉取与经原站拉取得到的对象是一致的。

---

### 3.5 阶段 E：认证与首次推送

#### 3.5.1 三次尝试的完整时间线

| 序号 | 使用的凭据来源 | GitHub 返回 | 结论 |
| --- | --- | --- | --- |
| 1 | 系统 Git config 中的 `credential.helper=manager`（GCM 已缓存 `EvanQuCN`） | `remote: Permission to biule/MinerU.git denied to EvanQuCN.`<br>`fatal: ... error: 403` | 认证通过，但账号**无写权限** |
| 2 | 用户提供的账号密码（`username` + `password`） | `remote: Invalid username or token. Password authentication is not supported for Git operations.` | 认证方式已废弃：**密码不能用于 Git 推送** |
| 3 | 用户提供的 PAT（`ghp_...`） | `8cd08422..ab3ef54d master -> master` | 成功 |

#### 3.5.2 为什么第一次会用到 `EvanQuCN`

首次执行推送时，命令没有屏蔽系统级 helper，Git 按配置调用了 `manager`（Git Credential Manager），而 Windows 凭据管理器里已经存在 `github.com` 的缓存凭据，属于账号 `EvanQuCN`。GitHub 明确返回该账号对 `biule/MinerU` 没有写权限。

这带来两个工程教训：

1. **凭据是按「主机」维度缓存的**，同一主机下多账号会互相干扰；
2. 排障时必须先**显式隔离凭据来源**，否则无法判断失败原因。

隔离方式（置空 helper 列表 + 注入临时 helper）：

```bash
git -c credential.helper= \
    -c credential.helper='!f() { ... }; f' \
    push origin master
```

#### 3.5.3 为什么密码不行

GitHub 于 **2021-08-13** 起移除了 HTTPS Git 操作的密码认证。现在可选：

- **Personal Access Token（classic）**：勾选 `repo` scope 即可读写仓库；
- **Fine-grained token**：按仓库授权，需要 `Contents: Read and write` 权限；
- **SSH key**：改用 `git@github.com`（本机虽有 `~/.ssh/id_rsa`，但当前网络下 SSH 22/443 经代理未打通）；
- **OAuth（GCM 浏览器授权）**：需要交互式浏览器。

本次使用 PAT，因为用户已提供且具备目标仓库写权限。

#### 3.5.4 推送命令的逐项解释

```bash
# -c credential.helper=
#   把从系统/全局配置继承来的 helper 列表清空（空字符串是 Git 规定的“重置”语义），
#   避免 GCM 中缓存的旧账号抢先应答。
#
# -c credential.helper='!f() { ... }; f'
#   以 "!" 开头的 helper 表示一段 shell 片段，由 Git 通过 sh 执行，并把操作类型作为第一个参数（$1）。
#   这里只在 get 时输出用户名/密码；store/erase 不做任何事（一次性使用，不落盘）。
#
# -c http.https://github.com.proxy=http://127.0.0.1:7892
#   仅对 https://github.com 生效的代理配置（Git 的 URL 级配置匹配）。
#
# push origin master
#   把本地 master 推送到 origin 的 master。
git -c credential.helper= \
    -c credential.helper='!f() { test "$1" = get && printf "%s\n" "username=$GIT_USER" "password=$GIT_TOKEN"; }; f' \
    -c http.https://github.com.proxy=http://127.0.0.1:7892 \
    push origin master
```

> 安全提示：上例从环境变量取值，避免 Token 出现在命令历史或 `ps` 输出中。本次排障时使用了一次性内联值，未写入任何文件。

#### 3.5.5 推送认证时序

```mermaid
sequenceDiagram
    autonumber
    participant Dev as 开发者
    participant Git as git
    participant GCM as Credential Manager
    participant Pxy as 本地代理端口 7892
    participant GH as GitHub

    Dev->>Git: git push origin master
    Git->>GCM: credential get（protocol=https, host=github.com）
    GCM-->>Git: username + PAT
    Git->>Pxy: CONNECT github.com:443
    Pxy->>GH: 建立隧道
    Git->>GH: GET /biule/MinerU.git/info/refs?service=git-receive-pack
    GH-->>Git: 200 + 现有 refs（含 Authorization 校验）

    alt 凭据有效且账号有写权限
        Git->>GH: POST /git-receive-pack（上传 pack）
        GH-->>Git: 更新 refs/heads/master
        Git-->>Dev: 8cd08422..ab3ef54d master -> master
    else 账号无写权限
        GH-->>Git: 403 Permission to biule/MinerU.git denied
    else 使用密码而非 Token
        GH-->>Git: 403 Password authentication is not supported
    end
```

---

### 3.6 阶段 F：凭据持久化（Git Credential Manager）

#### 3.6.1 不采用的方案

| 方案 | 问题 |
| --- | --- |
| 把 Token 写进 URL：`https://user:token@github.com/...` | 明文落入 `.git/config`；也会出现在日志/截图/备份中；轮换 Token 时需改配置 |
| `git config credential.helper store` | 明文保存到 `~/.git-credentials` |
| 环境变量 | 仅当前会话有效，适合脚本，不适合日常人工操作 |

#### 3.6.2 本次采用的方案

Git for Windows 的系统级配置中已有 `credential.helper=manager`（Git Credential Manager 2.7.3）。利用 Git 的凭据协议直接写入：

```bash
# approve 操作把凭据交给已配置的 helper 保存。
# 各字段以空行结束；密码字段即 PAT。
printf "protocol=https\nhost=github.com\nusername=jeffery.zz@outlook.com\npassword=$GITHUB_TOKEN\n\n" \
  | git credential approve
```

存储位置与加密：

```mermaid
flowchart LR
    G["git"] -->|"credential approve"| M["Git Credential Manager 2.7.3"]
    M -->|"写入 Generic Credentials"| W["Windows 凭据管理器"]
    W -->|"DPAPI 按当前用户加密"| D["磁盘凭据库"]
    G -->|"credential fill（后续 push）"| M
    M -->|"按 host 查找并解密"| W
```

性质说明：

- 凭据以**当前 Windows 用户**为边界加密（DPAPI）；其他用户无法读取。
- 同一用户下运行的其他程序理论上可以请求同一凭据——这是所有本机凭据存储的共性，不是 GCM 特有的缺陷。
- 典型条目名形如 `git:https://github.com`（实际命名以 GCM 实现为准）。

#### 3.6.3 校验存储结果（不打印明文）

```bash
# fill 会返回 username/password。此处只检查 username 与 token 是否匹配，
# 避免把密钥打印到终端或对话记录中。
out=$(printf "protocol=https\nhost=github.com\n\n" | git credential fill 2>/dev/null)
echo "$out" | grep '^username='
echo "$out" | grep -q "^password=$GITHUB_TOKEN$" \
  && echo "token-match: YES" || echo "token-match: NO"
```

#### 3.6.4 仓库级代理持久化

```bash
# 把代理写进仓库本地配置，后续 push/fetch 无需每次带 -c
git config --local http.https://github.com.proxy http://127.0.0.1:7892

# 确认（--local 只看仓库配置）
git config --local --get-regexp 'proxy|credential'
```

#### 3.6.5 端到端验证

```bash
# --dry-run：完整执行连接、认证、ref 协商，但不真正更新远端 ref。
# GIT_TERMINAL_PROMPT=0：禁止交互提示，确保失败时立即返回而不是等待输入。
GIT_TERMINAL_PROMPT=0 git push --dry-run origin master
```

本次结果：`Everything up-to-date`，退出码 0。说明 GCM 自动取到了有写权限的凭据，且代理链路可用。

---

### 3.7 阶段 G：提交文档并推送

#### 3.7.1 识别未跟踪文件

```bash
git status --porcelain=v1
```

本次输出：

```text
?? docs/tech/
```

目录内为 `docs/tech/windows-env-conda-setup.md`（Miniconda + uv 环境记录）。

#### 3.7.2 精确暂存

```bash
# 精确添加本次要提交的文件，避免把无关产物一并带入
git add docs/tech/windows-env-conda-setup.md

# 用 --short 复核暂存区内容
git status --short
```

#### 3.7.3 提交信息风格

该仓库使用 Conventional Commits 风格（例：`chore: sync recent releases in issue templates`）。文档类变更使用 `docs:` 前缀：

```bash
git commit -m "docs: add Windows Miniconda + uv environment setup notes"
```

本次结果：`ab3ef54d`，1 file changed，154 insertions。

#### 3.7.4 推送与远端校验

```bash
git push origin master

# 通过 mirror 读取远端 ref，独立确认推送结果（镜像会转发到上游）
git ls-remote mirror refs/heads/master
```

本次结果：

```text
   8cd08422..ab3ef54d  master -> master
ab3ef54d8ea002059649e82f1e1b281c3494a573    refs/heads/master
```

---

## 4. 源码与机制理解

### 4.1 Git 的 HTTPS 传输栈

```text
git push
  └─ git-remote-https（Git 的 HTTP(S) transport helper）
      └─ libcurl（TLS 后端：Schannel 或 OpenSSL）
          └─ TCP → [HTTP CONNECT 隧道] → TLS → GitHub
```

关键点：

- **代理配置的来源**：Git/libcurl 读取 `http.proxy` / `https_proxy` 等配置或环境变量，**不读取 Windows 的 Internet Settings 注册表**。因此浏览器能上 GitHub，不代表 `git` 能上。
- **URL 级配置匹配**：`http.<url>.*` 会按 scheme、host、port、path 逐段匹配。`http.https://github.com.proxy` 表示「所有指向 `https://github.com` 的请求」都使用该代理。
- **TLS 后端差异**：Schannel 是 Windows 原生实现，依赖系统证书库；OpenSSL 使用 Git 自带的 CA bundle。本次两者都因路径问题失败，证书校验本身正常，因此切换后端不是解药。

### 4.2 Git credential helper 协议

Git 与 helper 之间通过「标准输入输出 + key=value」通信。四种操作：

| 操作 | 触发时机 | 输入 | 期望输出 |
| --- | --- | --- | --- |
| `get` | 需要凭据时 | `protocol`、`host`（可能含 `path`、`username`） | `username=`、`password=` |
| `store` | 认证成功后 | 完整凭据 | 无 |
| `erase` | 认证失败/被拒绝后 | 完整凭据 | 无 |

`!` helper 的展开方式：

```bash
# 配置值以 "!" 开头时，Git 执行：sh -c "<感叹号之后的脚本>" <operation>
# 其中 $1 = get|store|erase，其余 key=value 从 stdin 读入。
# 下面的函数只在 get 时输出，避免把凭据写进任何存储。
!f() {
  test "$1" = get && printf "%s\n" "username=$GIT_USER" "password=$GIT_TOKEN"
}; f
```

逐行说明：

1. `!`：告诉 Git 这不是一个外部程序名，而是一段 shell 代码。
2. `f() { ... }; f`：定义后立即调用，确保逻辑在函数作用域内，且只执行一次。
3. `test "$1" = get`：仅响应读取操作；`store`/`erase` 静默成功。
4. `printf "%s\n" ...`：输出必须是 `key=value` 形式，每行一个键。

`credential.helper=` 置空的作用来自 Git 文档语义：**空字符串会重置 helper 列表**。因此下面的写法等价于「清空继承的 helper，只使用我指定的这个」：

```bash
git -c credential.helper= -c credential.helper='!f() { ... }; f' push
```

### 4.3 GCM 与 Windows 凭据管理器

- GCM 是一个实现了 credential helper 协议的独立程序；Git 只知道 `manager` 这个名字。
- 在 Windows 上，默认凭据存储是 Windows Credential Manager（Generic Credentials），条目由 DPAPI 按当前用户加密。
- `approve`/`fill`/`reject` 是 Git 提供的三个子命令，分别对应 `store`/`get`/`erase`，用于在不触发真实网络操作的情况下管理凭据。

常用管理命令：

```bash
# 删除该主机的已存凭据（会触发 helper 的 erase）
printf "protocol=https\nhost=github.com\n\n" | git credential reject

# 查看 GCM 版本
git credential-manager --version
```

### 4.4 gh-proxy 类镜像的转发原理（示意）

> 以下为**原理示意**，不是镜像站的真实源码；不同镜像实现细节不同，但核心行为一致。

```text
请求：
  https://gh-proxy.com/https://github.com/biule/MinerU.git/info/refs?service=git-upload-pack

处理（示意伪代码）：
  1. 取路径中第一个 "https://" 之后的部分作为上游 URL：
       upstream = "https://github.com/biule/MinerU.git/info/refs?service=git-upload-pack"
  2. 校验上游主机是否在白名单（github.com / raw.githubusercontent.com 等）
  3. 以 GET 转发（必要时附带 Range 支持断点续传）
  4. 原样回传状态码、响应头与响应体
```

因此：

- 它兼容 Git smart HTTP，所以 `git clone` / `ls-remote` 可用；
- 它本质是**读路径加速**，通常不代理 `git-receive-pack`，所以不适合作为 `push` 目标；
- 公共仓库无需携带 GitHub 凭据；私有仓库需要镜像站自身支持凭据透传（多数不支持）。

### 4.5 TUN + fake-IP 的工作方式

```mermaid
flowchart LR
    A["应用：resolve github.com"] --> B["代理的 DNS 劫持<br/>返回 198.18.0.11"]
    B --> C["应用连接 198.18.0.11:443"]
    C --> D["路由表把假地址流量导入 TUN 网卡"]
    D --> E["代理核心按映射表还原域名"]
    E --> F["经上游节点访问真实 GitHub"]
    F --> G["响应沿隧道返回"]
    E -.->|"核心故障 / 节点不可用"| X["假地址无真实主机<br/>连接超时或被拒绝"]
```

这解释了本次的核心矛盾：**DNS 解析「成功」不代表链路可用**，它可能只是代理核心给出的假地址。判断链路是否可用，必须继续做 TCP/TLS 层测试。

### 4.6 重试语义：clone 与 push 的幂等性

| 操作 | 幂等性 | 重试策略 |
| --- | --- | --- |
| `git clone <url> <dir>` | 对非空目录**不幂等**（直接拒绝） | 每次使用全新目录；成功后一次性发布 |
| `git fetch` | 幂等（只更新 refs 与对象库） | 可直接重试 |
| `git push` | 对 ref 更新是幂等的（远端比较新旧值） | 可直接重试；注意避免与其他人并发推送造成 non-fast-forward |

---

## 5. 扩展方案

### 5.1 其他镜像候选（本次实测）

| 镜像 | 本次状态 | 备注 |
| --- | --- | --- |
| `https://gh-proxy.com/https://github.com/...` | ✅ `ls-remote` 成功、克隆成功 | 本次采用 |
| `https://ghproxy.net/https://github.com/...` | ⚠️ 首页 200，Git 协议连接失败 | 可择机重试 |
| `https://gitclone.com/github.com/...` | ⚠️ 首页 200，Git 协议连接失败 | URL 形式不同，注意路径 |
| `https://ghfast.top/https://github.com/...` | ⚠️ 首页请求 403 | 可能需要特定路径或 UA |
| `https://kkgithub.com`、`https://bgithub.xyz`、`https://hub.gitmirror.com` | ❌ 不可达 | 已失效或不适用 |

> 镜像站具有时效性，建议每次使用前用 `git ls-remote <镜像URL>` 做最小验证。

### 5.2 SSH over 443 备选（本次未打通）

```bash
# 利用 Git for Windows 自带的 connect.exe 作为 ProxyCommand，
# 让 SSH 通过 HTTP 代理建立到 ssh.github.com:443 的连接。
ssh -o ProxyCommand="connect -H 127.0.0.1:7892 %h %p" \
    -p 443 -T git@ssh.github.com
```

本次返回 `Connection closed by UNKNOWN port 65535`，原因是代理在当时的故障窗口内无法完成 CONNECT，或代理规则不允许该目标。代理恢复后可再验证；SSH 方式的优点是无需 PAT，但需要把公钥登记到 GitHub。

### 5.3 代理端口变化

```bash
# 端口变化时只需更新仓库级配置
git config --local http.https://github.com.proxy http://127.0.0.1:<new-port>

# 不再需要代理时删除该项
git config --local --unset http.https://github.com.proxy
```

### 5.4 与上游同步（fork 场景）

`biule/MinerU` 是 `opendatalab/MinerU` 的 fork。如需同步上游：

```bash
# 上游直连同样被阻断，可把 upstream 配成镜像地址（仅用于 fetch）
git remote add upstream \
  "https://gh-proxy.com/https://github.com/opendatalab/MinerU.git"

git fetch upstream
git merge --ff-only upstream/master   # 或按需 rebase
git push origin master
```

### 5.5 多账号切换

```bash
# 1) 清除当前主机凭据
printf "protocol=https\nhost=github.com\n\n" | git credential reject

# 2) 以另一个账号写入
printf "protocol=https\nhost=github.com\nusername=<another-user>\npassword=<another-token>\n\n" \
  | git credential approve
```

注意：GCM 可能按用户名保存多条记录；若发现取到的账号不符合预期，务必先 `reject` 再 `approve`，或显式在 URL 中携带 `username@`。

### 5.6 离线迁移（bundle）

```bash
# 在可访问的机器上打包完整历史
git bundle create MinerU.bundle --all

# 在目标机器上从 bundle 克隆（不依赖网络）
git clone MinerU.bundle MinerU
```

适合网络长期不可用、或需要在多台隔离机器间传输的场景。

### 5.7 CI 环境中的凭据注入

```bash
# CI 中通常把 token 放在 secret 里，通过环境变量注入；
# 若使用 helper，注意不要在日志中回显。
export GIT_USER="x-access-token"
export GIT_TOKEN="$GITHUB_TOKEN"
git -c credential.helper= \
    -c credential.helper='!f() { test "$1" = get && printf "%s\n" "username=$GIT_USER" "password=$GIT_TOKEN"; }; f' \
    push origin master
```

---

## 6. 使用手册

### 6.1 日常命令

| 目的 | 命令 |
| --- | --- |
| 查看远端拓扑 | `git remote -v` |
| 查看分支跟踪状态 | `git status -sb` |
| 经镜像拉取 | `git fetch mirror` |
| 合并镜像最新 master | `git merge --ff-only mirror/master` |
| 经代理拉取原站 | `git fetch origin` |
| 推送 | `git push origin master` |
| 查看本地代理配置 | `git config --local --get http.https://github.com.proxy` |
| 验证推送链路（不改远端） | `GIT_TERMINAL_PROMPT=0 git push --dry-run origin master` |
| 校验仓库完整性 | `git fsck --no-progress` |

### 6.2 提交规范

1. 先 `git status --porcelain=v1` 查看变更；
2. 用精确路径 `git add <file>`，避免 `git add -A` 误收录构建产物；
3. 提交信息采用 Conventional Commits（`feat:` / `fix:` / `docs:` / `chore:` 等）；
4. 推送后通过 `git ls-remote mirror refs/heads/master` 或 `origin` 独立确认。

### 6.3 推送前的自检清单

```text
[ ] 当前分支是否是目标分支            git status -sb
[ ] 是否有未提交/未跟踪的预期外文件    git status --porcelain
[ ] 远端是否有新提交（避免 non-FF）    git fetch mirror && git log --oneline HEAD..mirror/master
[ ] 凭据是否为目标账号                 git credential fill（只看 username）
[ ] 代理链路是否可用                   GIT_TERMINAL_PROMPT=0 git push --dry-run origin master
```

---

## 7. 故障排查矩阵

| 现象 | 可能原因 | 处理 |
| --- | --- | --- |
| `schannel: failed to receive handshake` | 目标被阻断 / 代理隧道异常 | 测 TCP 443；换代理或镜像 |
| `SSL routines::unexpected eof while reading` | TLS 被中断（代理/中间设备） | 同上；确认证书不是问题（看 `verify result: 0`） |
| `Failed to connect ... via 127.0.0.1 ... Could not connect to server` | 代理核心异常/节点不可用 | 重启代理客户端；检查 7892；改用镜像 |
| `Connection refused` 但端口在 LISTENING | 代理接受队列异常/核心假死 | 重启代理；`Test-NetConnection` 复测 |
| `Permission to <repo> denied to <user>` | 账号无写权限 | 确认账号；让仓库所有者添加 Collaborator |
| `Invalid username or token` / `Password authentication is not supported` | 用了密码而非 PAT | 生成 PAT（`repo` 或 Contents 写权限） |
| `Everything up-to-date`（dry-run） | 本地与远端 ref 已一致 | 正常；无待推送提交 |
| `non-fast-forward` | 远端有新提交 | 先 `fetch` 再 `merge --rebase`/`merge` |
| 镜像 `ls-remote` 失败 | 镜像站失效/被限流 | 换候选镜像；重试；回退代理路径 |
| GCM 取到错误账号 | 同主机多账号缓存 | `git credential reject` 后重新 `approve` |
| 推送成功但镜像看不到新提交 | 镜像缓存/同步延迟 | 以 `origin` 的 `ls-remote` 或 GitHub 页面为准 |

---

## 8. 安全与合规

1. **最小权限**：优先使用 fine-grained PAT，仅授予目标仓库 `Contents: Read and write`；classic PAT 的 `repo` 权限范围更大。
2. **不落明文**：不要把 Token 写进 URL、`.git/config`、脚本或文档；本方案使用 GCM 加密存储。
3. **减少暴露面**：脚本中从环境变量读取 Token；避免 `set -x` 或日志回显凭据。
4. **轮换与吊销**：Token 应设置过期时间；一旦疑似泄露，立即在 GitHub 设置页吊销并重建。
5. **凭据边界**：Windows 凭据管理器按当前用户隔离；同一用户下的进程可请求凭据，因此不要以高权限账号运行不可信程序。
6. **代理信任**：本地代理能看到 HTTPS 的连接元数据，若开启 TLS 中间人（MITM）则能看到内容。使用第三方代理前应确认其可信度，并遵守所在组织的网络与数据合规要求。
7. **审计**：推送属于对外写操作，事前确认目标分支与提交内容；事后用远端 `ls-remote` 或平台记录核对。

---

## 9. 附录

### 9.1 本次操作时间线（2026-11-07）

| 阶段 | 关键动作 | 结果 |
| --- | --- | --- |
| A | 目录/配置/端口/进程勘察 | 定位代理 `127.0.0.1:7892`（`ziyoumaoCore`） |
| B | DNS/TCP/TLS/镜像分层诊断 | GitHub 直连阻断；代理间歇故障；`gh-proxy.com` 可用 |
| C | 经镜像克隆 | 成功，HEAD `8cd08422`，185.10 MiB，51,088 对象 |
| D | 远端读写分离 | `origin` = GitHub；`mirror` = gh-proxy |
| E | 三次认证尝试 | 缓存账号 403 → 密码被拒 → PAT 成功推送 |
| F | GCM 持久化 + 仓库级代理 | `fill` 校验通过；`--dry-run` 返回 up-to-date |
| G | 文档提交与推送 | `ab3ef54d` 推送成功，远端 ref 校验一致 |

### 9.2 关键值速查

| 键 | 值 |
| --- | --- |
| 克隆时远端 HEAD | `8cd08422` |
| 本次文档提交 | `ab3ef54d` |
| 代理混合端口 | `127.0.0.1:7892` |
| fake-IP 示例 | `198.18.0.11` |
| Git 版本 | `2.54.0.windows.1` |
| GCM 版本 | `2.7.3` |
| 认证方式 | Personal Access Token（classic） |

### 9.3 命令速查

```bash
# —— 拉取 ——
git fetch mirror
git merge --ff-only mirror/master

# —— 推送 ——
git push origin master

# —— 凭据 ——
printf "protocol=https\nhost=github.com\nusername=<user>\npassword=<token>\n\n" | git credential approve
printf "protocol=https\nhost=github.com\n\n" | git credential reject

# —— 链路验证 ——
GIT_TERMINAL_PROMPT=0 git push --dry-run origin master
git ls-remote mirror refs/heads/master

# —— 代理 ——
git config --local http.https://github.com.proxy http://127.0.0.1:7892
git config --local --unset http.https://github.com.proxy
```

---

## 附：MinerU 仓库速览

本方案落地后，工作目录即为完整的 MinerU 仓库。顶层结构（节选）：

| 路径 | 说明 |
| --- | --- |
| `mineru/` | 主 Python 包（`backend`、`cli`、`parser`、`model`、`tasks`、`render` 等） |
| `projects/` | 项目级说明与示例入口 |
| `docs/` | MkDocs 文档源（本次技术文档位于 `docs/tech/`） |
| `tests/` | 单元测试与集成测试 |
| `scripts/` | 构建/发布辅助脚本 |
| `docker/` | 容器化配置 |
| `skills/` | 仓库内置的 Agent 技能定义 |
| `pyproject.toml` | 依赖与工具链配置（Python >= 3.11, < 3.15） |
| `mkdocs.yml` | 文档站配置（Material + i18n） |

> 本文只涉及仓库的「获取 / 认证 / 推送」链路，不改变 MinerU 的 Python 源码结构；后续开发按 `CLAUDE.md` 规定的环境流程进行（本机已使用 conda 环境 `mineru`，见 `docs/tech/windows-env-conda-setup.md`）。
