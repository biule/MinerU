"""Render the teaching workspace Markdown documents as offline HTML pages.

The lessons and reference pages are hand-authored HTML. This script only renders
the Markdown documents (mission, resources, notes, learning records) into
matching `.html` files so they read well in a browser without a Markdown
extension or a network connection.

Usage:
    python docs/tech/teach/build_md_html.py
"""

from __future__ import annotations

import html
import itertools
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RECORDS = ROOT / "learning-records"

ROOT_NAV = """<nav class="topnav">
  <a href="index.html">首页</a>
  <a href="index.html#lessons">课程</a>
  <a href="reference/study-plan.html">学习路线</a>
  <a href="reference/faq.html">常见问题</a>
  <a href="reference/architecture-map.html">架构地图</a>
  <a href="reference/tier-matrix.html">档位矩阵</a>
  <a href="reference/glossary.html">术语表</a>
  <a href="reference/commands.html">命令速查</a>
  <a href="MISSION.html">使命</a>
  <a href="RESOURCES.html">资源</a>
  <a href="NOTES.html">笔记</a>
  <a href="learning-records/index.html">学习记录</a>
</nav>"""

RECORD_NAV = """<nav class="topnav">
  <a href="../index.html">首页</a>
  <a href="../index.html#lessons">课程</a>
  <a href="index.html">学习记录</a>
  <a href="../reference/study-plan.html">学习路线</a>
  <a href="../reference/faq.html">常见问题</a>
  <a href="../MISSION.html">使命</a>
  <a href="../RESOURCES.html">资源</a>
  <a href="../NOTES.html">笔记</a>
</nav>"""

BLOCK_START = re.compile(r"^(#{1,6})\s+|^```|^>\s?|^([-*+])\s+|^\d+\.\s+|^---+\s*$")
CODE_SPAN = re.compile(r"`([^`]+)`")
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
BOLD = re.compile(r"\*\*(.+?)\*\*")
_SLOT_COUNTER = itertools.count()


def rewrite_url(url: str, base_dir: Path) -> str:
    """把本工作区内的 Markdown/目录链接改写为已渲染的 HTML 链接。"""
    if url.startswith(("http://", "https://", "#", "mailto:", "/")):
        return url
    path, sep, anchor = url.partition("#")
    if not path:
        return url
    if path.endswith(".md"):
        candidate = (base_dir / path).with_suffix(".html")
        if candidate.exists():
            path = path[:-3] + ".html"
    elif path.endswith("/"):
        if (base_dir / path / "index.html").exists():
            path = path + "index.html"
    return path + (sep + anchor if sep else "")


def inline(text: str, base_dir: Path, *, allow_links: bool = True) -> str:
    """渲染行内代码、链接与粗体，先替换为占位符再转义。"""
    nonce = next(_SLOT_COUNTER)
    slots: list[str] = []

    def hold(fragment: str) -> str:
        slots.append(fragment)
        return f"\x00{nonce}:{len(slots) - 1}\x00"

    if allow_links:
        text = LINK.sub(
            lambda m: hold(
                f'<a href="{html.escape(rewrite_url(m.group(2), base_dir), quote=True)}">'
                f"{inline(m.group(1), base_dir, allow_links=False)}</a>"
            ),
            text,
        )
    text = CODE_SPAN.sub(lambda m: hold(f"<code>{html.escape(m.group(1), quote=False)}</code>"), text)
    text = html.escape(text, quote=False)
    text = BOLD.sub(r"<strong>\1</strong>", text)
    for index, fragment in enumerate(slots):
        text = text.replace(f"\x00{nonce}:{index}\x00", fragment)
    return text


def render_markdown(source: str, base_dir: Path) -> str:
    """把本工作区使用到的 Markdown 子集渲染为 HTML。"""
    lines = source.splitlines()
    out: list[str] = []
    paragraph: list[str] = []
    list_tag: str | None = None
    list_items: list[list[str]] = []
    quote: list[str] = []
    code: list[str] | None = None
    code_lang = ""
    first_paragraph = True

    def flush_paragraph() -> None:
        nonlocal paragraph, first_paragraph
        if not paragraph:
            return
        body = inline(" ".join(part.strip() for part in paragraph), base_dir)
        klass = ' class="lede"' if first_paragraph else ""
        out.append(f"<p{klass}>{body}</p>")
        first_paragraph = False
        paragraph = []

    def flush_list() -> None:
        nonlocal list_tag, list_items
        if not list_items or list_tag is None:
            list_tag, list_items = None, []
            return
        items = "\n".join(f"<li>{inline(' '.join(item), base_dir)}</li>" for item in list_items)
        out.append(f"<{list_tag}>\n{items}\n</{list_tag}>")
        list_tag, list_items = None, []

    def flush_quote() -> None:
        nonlocal quote
        if not quote:
            return
        out.append(f"<blockquote><p>{inline(' '.join(quote), base_dir)}</p></blockquote>")
        quote = []

    for line in lines:
        stripped = line.strip()

        if code is not None:
            if stripped.startswith("```"):
                language = f' class="language-{html.escape(code_lang)}"' if code_lang else ""
                out.append(f"<pre><code{language}>{html.escape(chr(10).join(code), quote=False)}</code></pre>")
                code = None
                code_lang = ""
            else:
                code.append(line)
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            flush_quote()
            code = []
            code_lang = stripped[3:].strip()
            continue

        if not stripped:
            flush_paragraph()
            flush_list()
            flush_quote()
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            flush_paragraph()
            flush_list()
            flush_quote()
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline(heading.group(2), base_dir)}</h{level}>")
            continue

        if re.match(r"^---+\s*$", stripped):
            flush_paragraph()
            flush_list()
            flush_quote()
            out.append("<hr>")
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            flush_list()
            quote.append(stripped[1:].strip())
            continue
        flush_quote()

        unordered = re.match(r"^[-*+]\s+(.*)$", stripped)
        ordered = re.match(r"^\d+\.\s+(.*)$", stripped)
        if unordered or ordered:
            flush_paragraph()
            tag = "ul" if unordered else "ol"
            if list_tag is not None and list_tag != tag:
                flush_list()
            list_tag = tag
            list_items.append([(unordered or ordered).group(1)])
            continue

        if list_items and line.startswith(("  ", "\t")):
            list_items[-1].append(stripped)
            continue
        if list_items:
            flush_list()

        paragraph.append(stripped)

    flush_paragraph()
    flush_list()
    flush_quote()
    if code is not None:
        out.append(f"<pre><code>{html.escape(chr(10).join(code), quote=False)}</code></pre>")
    return "\n".join(out)


def title_of(source: str, fallback: str) -> str:
    """取第一个一级标题作为页面标题。"""
    for line in source.splitlines():
        match = re.match(r"^#\s+(.*)$", line.strip())
        if match:
            return match.group(1)
    return fallback


def wrap_page(title: str, eyebrow: str, body: str, nav: str, source_name: str, footer_link: str) -> str:
    """套用与课程一致的 Tufte 风格页面外壳。"""
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — MinerU 4.1</title>
<link rel="stylesheet" href="{footer_link}assets/styles.css">
</head>
<body>
<div class="page">

{nav}

<p class="eyebrow">{html.escape(eyebrow)}</p>
{body}

<p class="footer">MinerU 4.1.7 · 教学文档 · <a href="{source_name}">Markdown 源</a> · <a href="{footer_link}index.html">课程目录</a></p>

</div>
</body>
</html>
"""


def render_root(name: str, eyebrow: str) -> None:
    """渲染根目录下的 Markdown 文档。"""
    source = (ROOT / f"{name}.md").read_text(encoding="utf-8")
    body = render_markdown(source, ROOT)
    page = wrap_page(title_of(source, name), eyebrow, body, ROOT_NAV, f"{name}.md", "")
    (ROOT / f"{name}.html").write_text(page, encoding="utf-8")


def render_records() -> None:
    """渲染 learning-records 下的 Markdown 文档。"""
    for source_path in sorted(RECORDS.glob("*.md")):
        source = source_path.read_text(encoding="utf-8")
        body = render_markdown(source, RECORDS)
        page = wrap_page(
            title_of(source, source_path.stem),
            "Teaching workspace · Learning record",
            body,
            RECORD_NAV,
            source_path.name,
            "../",
        )
        source_path.with_suffix(".html").write_text(page, encoding="utf-8")


def main() -> None:
    """生成全部 Markdown 的浏览器渲染版本。"""
    render_root("MISSION", "Teaching workspace · Mission")
    render_root("RESOURCES", "Teaching workspace · Resources")
    render_root("NOTES", "Teaching workspace · Notes")
    render_records()
    print("Rendered MISSION.html, RESOURCES.html, NOTES.html and learning-records/*.html")


if __name__ == "__main__":
    main()
