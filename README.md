# 정태현의 기술 기록

GitHub Pages로 운영하는 정적 기술 블로그입니다.

전략기획과 업무 시스템 설계에서 출발한 문제를 요구사항, 기술 제약, 데이터 흐름, 구현, 실패 원인과 검증으로 연결해 기록합니다. 제품이나 AI 에이전트를 소개하는 랜딩 페이지가 아니라 실제 기술 의사결정과 구현 경험을 읽는 공간을 지향합니다.

## 글의 방향

- 업무 요청, 승인, 정산과 기록 구조를 시스템 관점에서 설명합니다.
- 외부 데이터 원본, 내부 표준 모델, API 계약과 실패 경로를 구분합니다.
- AI가 맡는 판단과 사람이 검토해야 하는 지점을 함께 적습니다.
- 구현 결과뿐 아니라 실패 현상, 원인, 실행한 검증과 남은 한계를 남깁니다.
- 기획 글도 가능한 경우 `문제 정의 → 요구사항 → 기술 제약 → 설계 판단 → 구현 → 검증` 흐름으로 연결합니다.

모든 글에 같은 목차를 강제하지 않습니다. 글의 성격에 필요한 항목만 사용하되, 확인되지 않은 경험·수치·성과는 추가하지 않습니다.

## 정보 구조

```text
.
├─ index.html                  # 최근·대표 글과 기술 분야
├─ blog/
│  └─ index.html              # 전체 글 및 분야 필터
├─ about/
│  └─ index.html              # 짧은 소개와 대표 구현 기록
├─ posts/
│  └─ <post-slug>/
│     └─ index.html           # 기존 URL을 유지하는 개별 글
├─ assets/
│  ├─ css/site.css            # 공통 디자인과 글 본문 스타일
│  ├─ js/site.js              # 테마, 필터, 메타데이터, 목차
│  ├─ categories/             # 공개용 정물 이미지
│  └─ posts/                  # 글 안의 공개 다이어그램
├─ 404.html
├─ feed.xml                   # RSS 2.0
├─ sitemap.xml
├─ robots.txt
└─ sample-post.html
```

## 실제 글이 있는 기술 분야

- **시스템·업무 설계**: 요청·승인·정산, 주문 데이터, 내부 업무 구조
- **데이터·AI 시스템**: 공공데이터 정규화, 필터, LLM·Vision, 사람 검토
- **인터랙션·Vision**: AI 생성 과정, 영상 이벤트와 검증 로그

빈 카테고리는 만들지 않습니다. 새 글이 쌓여 독립된 분야가 되었을 때만 분류를 추가합니다.

## 게시글 구성

긴 글은 공통 스크립트가 본문의 `h2`를 읽어 목차를 만듭니다. 게시글의 `body`에는 다음 공개 메타데이터를 둡니다.

```html
<body
  data-page="post"
  data-category="데이터·AI 시스템"
  data-published="2026-07-02"
  data-updated="2026-07-17"
  data-read-time="8분"
>
```

새 글을 추가할 때는 description, canonical, Open Graph, 작성일·수정일·분야 메타데이터를 함께 작성하고 `blog/index.html`, `feed.xml`, `sitemap.xml`에서 연결합니다.

## 빌드와 로컬 확인

Jekyll, Hugo, Next.js를 사용하지 않습니다. `.nojekyll`을 둔 정적 HTML 사이트이며 별도 빌드 단계나 패키지 설치가 없습니다.

```powershell
python -m http.server 8000
```

브라우저에서 `http://127.0.0.1:8000/`을 확인합니다. 로컬 파일을 직접 열면 절대 경로 자산과 필터 쿼리를 정확히 검증하기 어려우므로 HTTP 서버 사용을 권장합니다.

확인할 화면:

1. 홈의 최근 글과 세 기술 분야
2. `/blog/` 목록 및 `?tag=` 필터
3. 긴 글의 목차, 코드 블록, 표와 이미지
4. 모바일 본문 폭과 긴 제목
5. `/sitemap.xml`, `/feed.xml`, `/robots.txt`, 존재하지 않는 URL의 404

## SEO와 분석

- 페이지별 title, description, canonical, Open Graph
- `sitemap.xml`, `robots.txt`, RSS `feed.xml`
- GA4 측정 ID `G-Z1WFWHS0VR`

GA4는 화면에 방문자 수를 표시하는 카운터가 아니라 보이지 않는 분석 코드입니다. 반영 여부는 배포된 HTML과 GA4 Realtime 또는 Tag Assistant에서 확인합니다.

## 배포

GitHub Pages는 `main` 브랜치 루트의 정적 파일을 제공합니다. 변경 사항을 검토하고 명시적으로 배포하기로 결정한 뒤에만 commit과 push를 수행합니다.

## 공개 범위

초안 Markdown, 개인 메모, 이력서 원문, 공모전·회사 내부 자료와 개인 경로는 이 공개 저장소에 추가하지 않습니다. 공개 가능한 사실과 이미지만 정리된 HTML 글에 포함합니다.
