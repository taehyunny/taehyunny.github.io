from __future__ import annotations

import argparse
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
READY_DIR = ROOT / "_drafts" / "ready"
POSTS_DIR = ROOT / "_posts"


TAG_RULES = {
    "cpp": ["c++", "cpp", "qt", "mfc", "pointer", "thread", "queue"],
    "qt": ["qt", "qpushbutton", "qstring", "qlocale"],
    "oop": ["객체", "인터페이스", "strategy", "pattern", "상속", "다형성"],
    "inheritance": ["상속", "inheritance"],
    "polymorphism": ["다형성", "polymorphism", "virtual", "override", "vtable", "vptr"],
    "memory": ["메모리", "padding", "패딩", "vptr", "vtable"],
    "strategy-pattern": ["strategy", "전략"],
    "sql": ["sql", "select", "join", "db", "database", "mariadb", "postgresql"],
    "spring": ["spring", "controller", "service", "repository"],
    "fastapi": ["fastapi"],
    "rag": ["rag", "vector", "qdrant", "embedding"],
    "docker": ["docker", "container"],
    "troubleshooting": ["error", "오류", "에러", "해결", "failed"],
}


@dataclass
class Draft:
    title: str
    date: datetime
    body: str
    categories: list[str]
    tags: list[str]


def strip_yaml_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not match:
        return {}, text

    raw_meta = match.group(1)
    body = text[match.end() :]
    meta: dict[str, str] = {}

    for line in raw_meta.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')

    return meta, body


def normalize_body(body: str) -> str:
    body = body.replace("\u200b", " ")
    body = body.replace("\xa0", " ")
    body = re.sub(r"^# Original Body\s*", "", body.strip(), flags=re.IGNORECASE)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip()


def extract_date(meta: dict[str, str], filename: str) -> datetime:
    match = re.search(r"(20\d{2})[.\-_ ]+(\d{1,2})[.\-_ ]+(\d{1,2})", filename)
    if match:
        year, month, day = (int(part) for part in match.groups())
        return datetime(year, month, day)

    for source in (meta.get("extractedAt"), meta.get("date")):
        if not source:
            continue
        try:
            return datetime.fromisoformat(source.replace("Z", "+00:00")).astimezone().replace(tzinfo=None)
        except ValueError:
            pass

    return datetime.now()


def clean_title(raw_title: str, fallback: str) -> str:
    title = raw_title or fallback
    title = re.sub(r"^\d{2,}-\d+-", "", title)
    title = re.sub(r"\.md$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s+", " ", title).strip()

    title = re.sub(r"20\d{2}\s*[.\-_ ]+\d{1,2}\s*[.\-_ ]+\d{1,2}", "", title).strip()
    title = title.strip("[] -_.")
    title = title.replace("[", "").replace("]", "").strip()

    if "버튼" in title and "객체" not in title:
        return "버튼 클릭 행위를 객체로 분리하는 설계 고민"
    if "상속" in title and "다형성" in title:
        return "C++ 상속과 다형성의 메모리 구조 정리"

    return title or "개발일지 정리"


def choose_categories_and_tags(title: str, body: str) -> tuple[list[str], list[str]]:
    haystack = f"{title}\n{body}".lower()
    tags: list[str] = []

    for tag, keywords in TAG_RULES.items():
        if any(keyword.lower() in haystack for keyword in keywords):
            tags.append(tag)

    if any(tag in tags for tag in ["rag", "fastapi"]):
        categories = ["ai-lab"]
    elif any(tag in tags for tag in ["cpp", "qt", "oop", "strategy-pattern", "inheritance", "polymorphism"]):
        categories = ["project-log", "architecture"]
    elif any(tag in tags for tag in ["spring", "sql"]):
        categories = ["backend"]
    elif "troubleshooting" in tags:
        categories = ["troubleshooting"]
    else:
        categories = ["project-log"]

    return categories, sorted(set(tags))


def slugify(text: str) -> str:
    lower_text = text.lower()
    if "버튼" in text and ("객체" in text or "클릭" in text):
        return "button-action-strategy"
    if "상속" in text and "다형성" in text:
        return "cpp-inheritance-polymorphism-memory"
    if "docker" in lower_text or "도커" in text:
        return "docker-troubleshooting"
    if "sql" in lower_text:
        return "sql-note"
    if "spring" in lower_text:
        return "spring-note"
    if "rag" in lower_text or "vector" in lower_text or "벡터" in text:
        return "rag-practice"

    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "post"


def structure_body(body: str) -> str:
    if "## " in body:
        return body

    # Keep the original content, but give it a readable technical-blog frame.
    return "\n\n".join(
        [
            "## 원문 메모",
            body,
            "## 배운 점",
            "- 원문을 바탕으로 추가 정리가 필요합니다.",
            "## 다음 과제",
            "- 코드 소유권, 예외 처리, 테스트 방법을 추가로 정리합니다.",
        ]
    )


def render_post(draft: Draft) -> str:
    date_value = draft.date.strftime("%Y-%m-%d %H:%M:%S +0900")
    categories = ", ".join(draft.categories)
    tags = ", ".join(draft.tags)

    return (
        "---\n"
        f'title: "{draft.title}"\n'
        f"date: {date_value}\n"
        f"categories: [{categories}]\n"
        f"tags: [{tags}]\n"
        "---\n\n"
        f"{draft.body.strip()}\n"
    )


def convert(path: Path, publish: bool) -> Path:
    text = path.read_text(encoding="utf-8")
    meta, body = strip_yaml_front_matter(text)
    body = normalize_body(body)
    date = extract_date(meta, path.name)
    title = clean_title(meta.get("title", ""), path.stem)
    categories, tags = choose_categories_and_tags(title, body)
    draft = Draft(
        title=title,
        date=date,
        body=structure_body(body),
        categories=categories,
        tags=tags,
    )

    target_dir = POSTS_DIR if publish else READY_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{date.strftime('%Y-%m-%d')}-{slugify(title)}.md"
    target.write_text(render_post(draft), encoding="utf-8")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert raw Markdown draft into a Chirpy post.")
    parser.add_argument("path", help="Path to raw Markdown draft")
    parser.add_argument("--publish", action="store_true", help="Write to _posts instead of _drafts/ready")
    args = parser.parse_args()

    target = convert(Path(args.path).resolve(), args.publish)
    print(target)


if __name__ == "__main__":
    main()
