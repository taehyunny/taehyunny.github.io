# 정태현 기술 블로그

GitHub Pages로 운영하는 개인 기술 블로그입니다. 백엔드, 운영, AI 실험, 프로젝트 회고를 정리하고, 장기적으로는 개인 지식관리 에이전트가 만든 Markdown 초안을 사람이 검수해 게시하는 흐름을 목표로 합니다.

## 현재 구성

- `index.html`: 기술 블로그 홈 화면
- `posts/`: 실제 배포되는 정적 글 페이지
- `_posts/`: Jekyll/Chirpy 형식의 원본 Markdown 글
- `_tabs/`: Chirpy 탭 설정
- `assets/css/taehyun-blog.css`: 블로그 전용 스타일
- `_drafts/`: 아직 게시하지 않은 글 초안

## 홈 화면 구조

현재 홈 화면은 기술 블로그 탐색에 맞춰 구성되어 있습니다.

- 블로그 소개
- 새로 나온 글
- 주제별 탐색
- 지식관리 에이전트 기반 작성 흐름
- 검색 가능한 전체 글 목록

카카오모빌리티 개발자 블로그처럼 최신 콘텐츠와 전체 콘텐츠를 분리하되, 개인 포트폴리오에 맞게 프로젝트·학습·AI 자동화 흐름을 강조했습니다.

## 글 작성 흐름

1. 학습 메모나 프로젝트 회고를 작성합니다.
2. R&D Knowledge Blog Agent가 메모를 분류하고 Markdown 초안을 생성합니다.
3. 사람이 초안을 검수하고 보완합니다.
4. `_posts/` 또는 `posts/`에 반영해 GitHub Pages로 게시합니다.

이 흐름은 완전 자동 게시가 아니라 Human-in-the-loop 방식을 전제로 합니다.

## 향후 개선 계획

- Jekyll 빌드 흐름과 정적 HTML 생성 흐름 정리
- R&D Knowledge Blog Agent의 초안을 `_drafts/ready/`로 자동 이동
- 카테고리별 랜딩 페이지 개선
- 글 검색 범위 확대
- 프로젝트 페이지를 포트폴리오 중심으로 재구성
- GitHub Actions 기반 빌드/배포 검증 추가

## 로컬 확인

정적 HTML만 확인할 때는 루트의 `index.html`을 브라우저에서 열면 됩니다.

Jekyll로 확인할 경우 Ruby/Bundler 환경에서 아래 명령을 사용할 수 있습니다.

```bash
bundle install
bundle exec jekyll serve
```
