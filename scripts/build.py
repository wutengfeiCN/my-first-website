#!/usr/bin/env python3
"""从 content/notes/*.md 生成笔记页、归档、RSS、sitemap，并刷新首页列表。

用法：
    python3 scripts/build.py            # 构建 + 重新生成字体子集
    python3 scripts/build.py --no-font  # 只构建，不动字体

依赖：Markdown、PyYAML；字体子集需要 fonttools + brotli。
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, time, timezone
from email.utils import format_datetime
from itertools import groupby
from pathlib import Path

try:
    import markdown
    import yaml
except ImportError:
    sys.exit(
        "缺少构建依赖。先运行：\n"
        "  python3 -m venv .venv\n"
        "  .venv/bin/pip install -r requirements.txt"
    )

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "notes"
TEMPLATE = ROOT / "scripts" / "templates" / "page.html"
BASE = "https://wutengfeiCN.github.io/my-first-website"
SITE_NAME = "阿奔 · 以技载道"


# ---------- 读取与校验 ----------

def load_notes() -> list[dict]:
    notes = []
    for path in sorted(CONTENT.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
        if not m:
            sys.exit(f"[build] {path.name}: 缺少 front matter（--- ... ---）")
        meta = yaml.safe_load(m.group(1)) or {}
        for key in ("title", "date", "summary"):
            if not meta.get(key):
                sys.exit(f"[build] {path.name}: front matter 缺少 {key}")
        try:
            meta["date"] = date.fromisoformat(str(meta["date"]))
        except ValueError:
            sys.exit(f"[build] {path.name}: date 必须是 YYYY-MM-DD")
        if not path.stem.startswith(meta["date"].isoformat()):
            sys.exit(f"[build] {path.name}: 文件名必须以日期开头，例如 {meta['date']}-slug.md")
        meta["slug"] = path.stem
        meta["tags"] = meta.get("tags") or []
        if isinstance(meta["tags"], str):
            meta["tags"] = [t.strip() for t in meta["tags"].split(",") if t.strip()]
        meta["subtitle"] = meta.get("subtitle", "")
        meta["source"] = path.name
        meta["md"] = m.group(2).strip()
        notes.append(meta)

    if not notes:
        sys.exit("[build] content/notes/ 下没有 .md 文件")

    notes.sort(key=lambda n: (n["date"], n["slug"]), reverse=True)
    dates = [n["date"] for n in notes]
    if len(dates) != len(set(dates)):
        print("[build] 警告：有多篇文章日期相同，归档顺序按文件名倒序", file=sys.stderr)
    return notes


# ---------- Markdown ----------

LINK_RE = re.compile(r'<a href="(https?://[^"]+)">')


def render_markdown(text: str) -> str:
    md = markdown.Markdown(extensions=["extra", "sane_lists"], output_format="html5")
    out = md.convert(text)

    def external(m: re.Match) -> str:
        url = m.group(1)
        if "wutengfeiCN.github.io" in url:
            return m.group(0)
        return f'<a href="{url}" target="_blank" rel="noopener noreferrer">'

    return LINK_RE.sub(external, out)


def plain_length(html_text: str) -> int:
    text = re.sub(r"<[^>]+>", "", html_text)
    return len(re.sub(r"\s+", "", html.unescape(text)))


def reading_minutes(chars: int) -> int:
    return max(1, round(chars / 350))


def date_cn(d: date) -> str:
    return f"{d.year} 年 {d.month} 月 {d.day} 日"


def dotted(d: date) -> str:
    return d.strftime("%Y.%m.%d")


# ---------- 片段 ----------

def tags_html(tags: list[str]) -> str:
    return "".join(f'<span class="tag">{html.escape(t)}</span>' for t in tags)


def meta_tags(tags: list[str]) -> str:
    if not tags:
        return ""
    return f'<span class="meta-tags">{tags_html(tags)}</span>'



def epigraph_html(note: dict) -> str:
    text = note.get("epigraph")
    if not text:
        return ""
    source = note.get("epigraph_source", "")
    cite = f'<figcaption>{html.escape(source)}</figcaption>' if source else ""
    return f'''      <figure class="epigraph">
        <blockquote><p>{html.escape(text)}</p></blockquote>
        {cite}
      </figure>

'''


def article_body(note: dict, content: str, newer: dict | None, older: dict | None, updated: str) -> str:
    chars = plain_length(content)
    newer_html = (
        f'<a href="{newer["slug"]}.html"><span class="label">较新一篇</span>{html.escape(newer["title"])}</a>'
        if newer else "<span></span>"
    )
    older_html = (
        f'<a class="next" href="{older["slug"]}.html"><span class="label">较早一篇</span>{html.escape(older["title"])}</a>'
        if older else ""
    )
    return f'''  <div class="wrap">
    <nav class="breadcrumb" aria-label="面包屑">
      <a href="../index.html">首页</a><span class="sep">/</span><a href="./">笔记</a><span class="sep">/</span><span>{html.escape(note["title"])}</span>
    </nav>

    <article>
      <header class="article-head">
        <p class="kicker">笔记 · {note["date"].isoformat()}</p>
        <h1>{html.escape(note["title"])}</h1>
        <p class="lede">{html.escape(note["subtitle"])}</p>
        <p class="article-meta" style="margin-top:18px">
          <time datetime="{note["date"].isoformat()}">{date_cn(note["date"])}</time>
          <span>约 {chars:,} 字</span>
          <span>{reading_minutes(chars)} 分钟</span>
          {meta_tags(note["tags"])}
        </p>
      </header>

{epigraph_html(note)}      <div class="prose">
{content}
      </div>

      <footer class="article-foot">
        <p class="meta-line">标签：{tags_html(note["tags"])}</p>
        <nav class="article-nav" aria-label="文章翻页">
          {newer_html}
          {older_html}
        </nav>
      </footer>
    </article>
  </div>'''


def homepage_rows(notes: list[dict]) -> str:
    rows = []
    for n in notes[:3]:
        rows.append(f'''        <article class="note-row">
          <p class="note-date">{n["date"].isoformat()}</p>
          <div>
            <h3><a href="notes/{n["slug"]}.html">{html.escape(n["title"])}</a></h3>
            <p>{html.escape(n.get("home_summary") or n["summary"])}</p>
          </div>
          <span class="note-arrow" aria-hidden="true">→</span>
        </article>''')
    return "\n\n".join(rows) + "\n"


def notes_index_body(notes: list[dict], updated: str) -> str:
    rows = []
    for year, group in groupby(notes, key=lambda n: n["date"].year):
        items = []
        for n in group:
            items.append(f'''        <article class="note-row" id="{n["slug"]}">
          <p class="note-date"><time datetime="{n["date"].isoformat()}">{n["date"].isoformat()}</time></p>
          <div>
            <h3><a href="{n["slug"]}.html">{html.escape(n["title"])}</a></h3>
            <p>{html.escape(n["summary"])}</p>
            <p class="note-tags">{tags_html(n["tags"])}</p>
          </div>
          <span class="note-arrow" aria-hidden="true">→</span>
        </article>''')
        rows.append(f'    <h2 class="year-label">{year}</h2>\n    <div class="note-list">\n' + "\n\n".join(items) + "\n    </div>")
    return f'''  <div class="wrap">
    <header class="page-head">
      <p class="kicker">笔记</p>
      <h1>工程里的取舍，书页里的分寸</h1>
      <p class="lede">记录做过的项目、想清楚的问题、读过的书。不定期更新，按时间倒序。</p>
      <p class="meta-line"><span>{len(notes)} 篇</span><span>更新于 {updated}</span><a href="../rss.xml">RSS 订阅</a></p>
    </header>

{chr(10).join(rows)}
  </div>'''


# ---------- 结构化数据 ----------

def article_jsonld(note: dict, chars: int) -> str:
    url = f'{BASE}/notes/{note["slug"]}.html'
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BlogPosting",
                "headline": note["title"],
                "description": note["summary"],
                "datePublished": note["date"].isoformat(),
                "dateModified": note["date"].isoformat(),
                "inLanguage": "zh-CN",
                "wordCount": chars,
                "author": {"@type": "Person", "name": "阿奔", "url": f"{BASE}/"},
                "publisher": {"@type": "Person", "name": "阿奔"},
                "image": f"{BASE}/assets/og-cover.png",
                "mainEntityOfPage": {"@type": "WebPage", "@id": url},
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "首页", "item": f"{BASE}/"},
                    {"@type": "ListItem", "position": 2, "name": "笔记", "item": f"{BASE}/notes/"},
                    {"@type": "ListItem", "position": 3, "name": note["title"]},
                ],
            },
        ],
    }
    return '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + "\n</script>"


def notes_jsonld() -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "笔记",
        "url": f"{BASE}/notes/",
        "description": "工程里的取舍，书页里的分寸。",
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": f"{BASE}/"},
    }
    return '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + "\n</script>"


# ---------- 模板 ----------

def fill(template: str, mapping: dict[str, str]) -> str:
    out = template
    for key, value in mapping.items():
        out = out.replace("{{" + key + "}}", value)
    leftover = set(re.findall(r"\{\{([A-Z_]+)\}\}", out))
    if leftover:
        sys.exit(f"[build] 模板有未替换的占位符：{', '.join(sorted(leftover))}")
    return out


def page_common(updated: str) -> dict[str, str]:
    return {
        "BASE": BASE,
        "ASSETS": "../assets",
        "HOME": "../index.html",
        "NOTES": "./",
        "ABOUT": "../about.html",
        "CONTACT": "../index.html#contact",
        "RSS": "../rss.xml",
        "PROJECTS": "../projects/",
        "UPDATED": updated,
        "ACTIVE_HOME": "",
        "ACTIVE_NOTES": "",
        "ACTIVE_ABOUT": "",
        "EXTRA_META": "",
    }


# ---------- 输出 ----------

def write_articles(notes: list[dict], template: str, updated: str) -> None:
    for i, note in enumerate(notes):
        content = render_markdown(note["md"])
        chars = plain_length(content)
        newer = notes[i - 1] if i > 0 else None
        older = notes[i + 1] if i + 1 < len(notes) else None
        mapping = page_common(updated)
        mapping.update({
            "TITLE": f'{note["title"]}｜阿奔',
            "DESC": note["summary"],
            "CANONICAL": f'{BASE}/notes/{note["slug"]}.html',
            "OGTYPE": "article",
            "EXTRA_META": (
                f'<meta property="article:published_time" content="{note["date"].isoformat()}">\n'
                '<meta property="article:author" content="阿奔">'
            ),
            "JSONLD": article_jsonld(note, chars),
            "ACTIVE_NOTES": ' aria-current="page"',
            "BODY": article_body(note, content, newer, older, updated),
        })
        out = fill(template, mapping)
        (ROOT / "notes" / f'{note["slug"]}.html').write_text(out, encoding="utf-8")


def write_notes_index(notes: list[dict], template: str, updated: str) -> None:
    mapping = page_common(updated)
    mapping.update({
        "TITLE": "笔记｜阿奔",
        "DESC": "工程里的取舍，书页里的分寸。记录做过的项目、想清楚的问题、读过的书。",
        "CANONICAL": f"{BASE}/notes/",
        "OGTYPE": "website",
        "JSONLD": notes_jsonld(),
        "ACTIVE_NOTES": ' aria-current="page"',
        "BODY": notes_index_body(notes, updated),
    })
    (ROOT / "notes" / "index.html").write_text(fill(template, mapping), encoding="utf-8")


def update_homepage(notes: list[dict], updated: str) -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"(<!-- NOTES:START -->)(.*?)(<!-- NOTES:END -->)", re.S)
    if not pattern.search(text):
        sys.exit("[build] index.html 缺少 <!-- NOTES:START --> ... <!-- NOTES:END --> 标记")
    text = pattern.sub(lambda m: m.group(1) + "\n" + homepage_rows(notes) + "        " + m.group(3), text)
    text = re.sub(r"最近更新 \d{4}\.\d{2}\.\d{2}", f"最近更新 {updated}", text)
    path.write_text(text, encoding="utf-8")

    about = ROOT / "about.html"
    a = about.read_text(encoding="utf-8")
    a = re.sub(r"更新于 \d{4}\.\d{2}\.\d{2}", f"更新于 {updated}", a)
    a = re.sub(r"最近更新 \d{4}\.\d{2}\.\d{2}", f"最近更新 {updated}", a)
    about.write_text(a, encoding="utf-8")


def write_rss(notes: list[dict], updated: str) -> None:
    items = []
    for n in notes:
        dt = datetime.combine(n["date"], time.min).replace(tzinfo=timezone.utc)
        body = render_markdown(n["md"]).replace("]]>", "]]&gt;")
        items.append(f'''    <item>
      <title>{html.escape(n["title"])}</title>
      <link>{BASE}/notes/{n["slug"]}.html</link>
      <guid isPermaLink="true">{BASE}/notes/{n["slug"]}.html</guid>
      <pubDate>{format_datetime(dt)}</pubDate>
      <description>{html.escape(n["summary"])}</description>
      <content:encoded><![CDATA[{body}]]></content:encoded>
    </item>''')
    last = datetime.combine(notes[0]["date"], time.min).replace(tzinfo=timezone.utc)
    rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>阿奔的笔记</title>
    <link>{BASE}/notes/</link>
    <description>工程里的取舍，书页里的分寸。</description>
    <language>zh-CN</language>
    <lastBuildDate>{format_datetime(last)}</lastBuildDate>
    <atom:link href="{BASE}/rss.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
  </channel>
</rss>
'''
    (ROOT / "rss.xml").write_text(rss, encoding="utf-8")


def write_sitemap(notes: list[dict], latest_iso: str) -> None:
    urls = [("", latest_iso, "1.0"), ("notes/", latest_iso, "0.9"), ("about.html", latest_iso, "0.7")]
    if (ROOT / "projects" / "index.html").exists():
        urls.append(("projects/", latest_iso, "0.8"))
    for n in notes:
        urls.append((f'notes/{n["slug"]}.html', n["date"].strftime("%Y-%m-%d"), "0.8"))
    body = "\n".join(
        f"  <url>\n    <loc>{BASE}/{u}</loc>\n    <lastmod>{d}</lastmod>\n    <priority>{p}</priority>\n  </url>"
        for u, d, p in urls
    )
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{body}
</urlset>
'''
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")


def run_font_subset() -> None:
    local = Path(sys.executable).with_name("pyftsubset")
    tool = str(local) if local.exists() else shutil.which("pyftsubset")
    if not tool:
        print("[build] 跳过字体子集：未找到 pyftsubset，安装方式见 README", file=sys.stderr)
        return
    env = os.environ.copy()
    env["PATH"] = str(Path(tool).parent) + os.pathsep + env.get("PATH", "")
    subprocess.run([str(ROOT / "scripts" / "subset-font.sh")], check=True, cwd=ROOT, env=env)


def main() -> None:
    parser = argparse.ArgumentParser(description="生成笔记站")
    parser.add_argument("--no-font", action="store_true", help="跳过字体子集")
    args = parser.parse_args()

    notes = load_notes()
    updated = dotted(notes[0]["date"])
    template = TEMPLATE.read_text(encoding="utf-8")

    write_articles(notes, template, updated)
    write_notes_index(notes, template, updated)
    update_homepage(notes, updated)
    write_rss(notes, updated)
    write_sitemap(notes, notes[0]["date"].isoformat())

    print(f"[build] {len(notes)} 篇笔记 → notes/、rss.xml、sitemap.xml，更新于 {updated}")

    if not args.no_font:
        run_font_subset()


if __name__ == "__main__":
    main()
