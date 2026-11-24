# 课程导航整理（1-11 课串联）

日期：2026-07-27

## 完成的事
- 修补 1-3 课缺失的"下一课"链接（原文件都是 `<span></span>` 占位）
- 修正第 4 课错误的 prev 链接（原指向不存在的 `0003-configuration-deep-dive.html`，改为正确的 `0003-configuration.html`）
- 给第 9 课的"下一课待续"补上第 10 课链接
- 给第 10 课、第 11 课补完整 prev/next 导航（原本完全没有 nav 区）
- 第 1 课加入"↑ 课程总目录"回链
- 新建 `teach/lessons/index.html` 课程总目录，按"建立认知 / 动手用起来 / 读源码调试 / 扩展跃迁"四阶段组织 11 课，每课一张 lesson-card，含日期、阅读时间、关键词

## Why
- 学习路径应该可被浏览器反向回溯，让用户任意一节跳进来都能找到上下文
- 之前 1-3 课 nav 区只有占位空 span，目录到第 3 课就断了；10-11 课写完后没补 nav，从第 9 课继续会卡死
- 课程主题跨度从"什么是 PDF 解析"到"WSL2 跑 vLLM"，需要一个总览页让读者看清自己处于哪个阶段

## How to apply
- 未来新增第 12+ 课，**必须**在新建 HTML 时加 `.lesson-nav` 区，prev 指向上一课、next 留空或指向 index.html
- 同时回到前一课把它的 next 补上（避免出现"下一课待续"这种过时占位）
- index.html 新增课程时同步追加 lesson-card，保持四阶段结构或重新组织阶段
- **路径关键提醒**：`index.html` 自己位于 `teach/lessons/` 目录内，所以内部链接**不要**再加 `lessons/` 前缀（否则浏览器解析为 `lessons/lessons/xxx.html` 失效）；CSS 路径要用 `../assets/lesson.css`（与各课一致），不是 `assets/lesson.css`

## Implications
- 11 课现在形成了首尾相接的可线性阅读路径，加上 index.html 可选起点
- 后续如果做学习地图、二维码分享课程，可以指向 index.html
- 这一改动不改各课正文，只是套件层面的导航修复