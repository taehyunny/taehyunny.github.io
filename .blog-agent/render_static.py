from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "_posts"
STATIC_POSTS_DIR = ROOT / "posts"


@dataclass
class Post:
    title: str
    date: str
    categories: list[str]
    tags: list[str]
    slug: str
    body: str


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not match:
        return {}, text

    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')

    return meta, text[match.end() :]


def parse_list(value: str) -> list[str]:
    value = value.strip()
    if not value.startswith("["):
        return []
    return [item.strip().strip("'\"") for item in value.strip("[]").split(",") if item.strip()]


def slug_from_filename(path: Path) -> str:
    return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)


def load_posts() -> list[Post]:
    posts: list[Post] = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        title = meta.get("title", path.stem)
        raw_date = meta.get("date", "1970-01-01")
        date = raw_date[:10]
        posts.append(
            Post(
                title=title,
                date=date,
                categories=parse_list(meta.get("categories", "[]")),
                tags=parse_list(meta.get("tags", "[]")),
                slug=slug_from_filename(path),
                body=body.strip(),
            )
        )
    posts.sort(key=lambda item: item.date, reverse=True)
    return posts


def md_inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    paragraph: list[str] = []
    in_code = False
    code_lines: list[str] = []
    in_list = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            out.append(f"<p>{md_inline(' '.join(paragraph))}</p>")
            paragraph = []

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    for line in lines:
        if line.startswith("```"):
            if in_code:
                out.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines = []
                in_code = False
            else:
                flush_paragraph()
                close_list()
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            close_list()
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            close_list()
            out.append(f"<h2>{md_inline(stripped[3:])}</h2>")
        elif stripped.startswith("### "):
            flush_paragraph()
            close_list()
            out.append(f"<h3>{md_inline(stripped[4:])}</h3>")
        elif stripped.startswith("- "):
            flush_paragraph()
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{md_inline(stripped[2:])}</li>")
        elif stripped.startswith("> "):
            flush_paragraph()
            close_list()
            out.append(f"<blockquote>{md_inline(stripped[2:])}</blockquote>")
        else:
            paragraph.append(stripped)

    flush_paragraph()
    close_list()
    return "\n".join(out)


def sidebar(active: str = "") -> str:
    items = [
        ("홈", "/"),
        ("프로젝트", "/projects.html"),
        ("카테고리", "/categories.html"),
        ("태그", "/tags.html"),
        ("아카이브", "/archives.html"),
        ("소개", "/about.html"),
    ]
    links = "\n".join(
        f'<a class="{"active" if active == label else ""}" href="{href}">{label}</a>'
        for label, href in items
    )
    return f"""
<aside class="sidebar">
  <div class="avatar"></div>
  <h1 class="brand">정태현</h1>
  <p class="tagline">Backend, Operations, AI Lab</p>
  <nav class="nav">{links}</nav>
  <div class="social">
    <a href="https://github.com/taehyunny">GH</a>
    <a href="mailto:taehyunny0312@gmail.com">@</a>
    <a href="/feed.xml">RSS</a>
  </div>
</aside>
"""


def page(title: str, body: str, active: str = "") -> str:
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} | 정태현 기술 블로그</title>
  <link rel="stylesheet" href="/assets/css/taehyun-blog.css">
</head>
<body>
  <div class="layout">
    {sidebar(active)}
    <main class="content">{body}</main>
  </div>
</body>
</html>
"""


def post_card(post: Post) -> str:
    tags = "".join(f'<span class="tag">{html.escape(tag)}</span>' for tag in post.tags[:6])
    return f"""
<a class="post-card" href="/posts/{post.slug}/">
  <h2>{html.escape(post.title)}</h2>
  <div class="meta">{post.date} · {", ".join(post.categories)}</div>
  <div class="tags">{tags}</div>
</a>
"""


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render() -> None:
    posts = load_posts()

    home = f"""
<section class="hero">
  <div class="eyebrow">Technical Blog</div>
  <h1>운영과 백엔드, AI 서비스를 연결하는 개발자로 성장하는 기록</h1>
  <p class="lead">비전공자로 시작해 C++/Python 프로젝트를 경험했고, 웹 SI/SM 실무와 SQL, 로그 분석, AI 백엔드 실습을 쌓아가는 과정을 정리합니다.</p>
</section>
<section class="post-list">
  {''.join(post_card(post) for post in posts)}
</section>
"""
    write(ROOT / "index.html", page("홈", home, "홈"))

    about = """
<section class="hero">
  <div class="eyebrow">About</div>
  <h1>정태현</h1>
  <p class="lead">현재는 웹 SI/SM 실무 기반을 쌓고, 장기적으로는 AI 기능을 안정적으로 서비스에 붙이는 MLOps/LLMOps 개발자를 목표로 합니다.</p>
</section>
<div class="grid">
  <div class="panel"><h2>Focus</h2><ul><li>Backend: Java/Spring, API, SQL</li><li>Operations: log analysis, troubleshooting, deployment flow</li><li>AI Lab: FastAPI, RAG, Vector DB, LLM API</li><li>Goal: MLOps / LLMOps Engineer</li></ul></div>
  <div class="panel"><h2>Writing</h2><p>완성된 정답보다 문제를 이해하고 해결해가는 과정을 기록합니다. 왜 그렇게 설계했는지, 어떤 로그와 데이터를 확인했는지, 다음에는 무엇을 다르게 할지에 집중합니다.</p></div>
</div>
"""
    write(ROOT / "about.html", page("소개", about, "소개"))

    projects = """
<section class="hero"><div class="eyebrow">Projects</div><h1>프로젝트 기록</h1><p class="lead">이력서와 연결되는 프로젝트 경험을 기술 관점으로 정리합니다.</p></section>
<div class="grid">
  <div class="panel"><h2>AI Backend Lab</h2><p>FastAPI, PostgreSQL, Qdrant, Docker Compose를 이용해 RAG 기반 AI 백엔드 흐름을 실습합니다.</p></div>
  <div class="panel"><h2>배달 플랫폼</h2><p>C++ TCP/IP 서버와 MariaDB를 기반으로 주문/결제 데이터 흐름과 서버 검증 구조를 설계했습니다.</p></div>
  <div class="panel"><h2>감정 기반 AI 에이전트</h2><p>OpenCV, PyTorch, FastAPI를 연결해 표정 인식과 LLM 응답 구조를 실험했습니다.</p></div>
  <div class="panel"><h2>낙상 방지 시스템</h2><p>CircularBuffer와 ThreadSafeQueue를 활용해 실시간 영상 처리와 이벤트 기록 구조를 설계했습니다.</p></div>
</div>
"""
    write(ROOT / "projects.html", page("프로젝트", projects, "프로젝트"))

    category_map: dict[str, list[Post]] = {}
    tag_map: dict[str, list[Post]] = {}
    for post in posts:
        for category in post.categories:
            category_map.setdefault(category, []).append(post)
        for tag in post.tags:
            tag_map.setdefault(tag, []).append(post)

    categories = "<section class='hero'><h1>카테고리</h1></section>" + "".join(
        f"<h2>{html.escape(name)}</h2><div class='post-list'>{''.join(post_card(post) for post in items)}</div>"
        for name, items in sorted(category_map.items())
    )
    write(ROOT / "categories.html", page("카테고리", categories, "카테고리"))

    tags = "<section class='hero'><h1>태그</h1></section>" + "".join(
        f"<h2>#{html.escape(name)}</h2><div class='post-list'>{''.join(post_card(post) for post in items)}</div>"
        for name, items in sorted(tag_map.items())
    )
    write(ROOT / "tags.html", page("태그", tags, "태그"))

    archives = "<section class='hero'><h1>아카이브</h1></section><div class='post-list'>" + "".join(
        post_card(post) for post in posts
    ) + "</div>"
    write(ROOT / "archives.html", page("아카이브", archives, "아카이브"))

    for post in posts:
        body = f"""
<article class="article">
  <div class="meta">{post.date} · {", ".join(post.categories)}</div>
  <h1>{html.escape(post.title)}</h1>
  <div class="tags">{''.join(f'<span class="tag">{html.escape(tag)}</span>' for tag in post.tags)}</div>
  {markdown_to_html(post.body)}
</article>
"""
        write(ROOT / "posts" / post.slug / "index.html", page(post.title, body))


if __name__ == "__main__":
    render()
