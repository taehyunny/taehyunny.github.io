# Blog Agent

개발일지 Markdown 파일을 Jekyll Chirpy 블로그 포스트 형태로 정리하기 위한 로컬 도구입니다.

## 폴더 역할

```text
_drafts/raw/     원본 개발일지
_drafts/ready/   검토용 정리 초안
_posts/          실제 발행 글
```

## 사용 방법

원본 Markdown 파일을 `_drafts/raw/`에 넣은 뒤:

```powershell
python .blog-agent/publish_draft.py "_drafts/raw/원본파일.md"
```

발행까지 바로 하려면:

```powershell
python .blog-agent/publish_draft.py "_drafts/raw/원본파일.md" --publish
```

## 중요한 한계

이 스크립트는 형식 자동화 도구입니다.

- YAML front matter 생성
- 제목/날짜 추출
- 카테고리/태그 추천
- 코드블록 후보 정리
- 원본 메타데이터 제거
- `_drafts/ready` 또는 `_posts` 파일 생성

글의 깊은 편집, 문체 정리, 보안 판단은 Codex와 함께 최종 검토하는 것을 권장합니다.

