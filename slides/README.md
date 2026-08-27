# 강의 슬라이드 (RevealJS)

책 내용을 기반으로 만드는 **강의용 슬라이드**입니다. 참고한 강의 스타일(흰 배경·두꺼운 볼드 제목·알록달록 강조·핑크 알약 라벨·컬러 콜아웃)을 적용했습니다.

## 구성
- `theme.scss` — 강의 슬라이드 테마(공통)
- `week01-slides.qmd` — 1주차 예시 덱(**템플릿**). 새 주차는 이걸 복사해 내용만 바꾸면 됩니다.

## 렌더링
```bash
# 개별 덱 렌더 (책과 별도로)
quarto render slides/week01-slides.qmd
# 미리보기
quarto preview slides/week01-slides.qmd
```
결과는 `week01-slides.html` (브라우저에서 열기). `Q`.. 아니, 발표 중 `F`=전체화면, `S`=발표자 노트, `ESC`=슬라이드 개요.

## PDF/PPT로 내보내기
- **PDF**: 브라우저에서 슬라이드 URL 뒤에 `?print-pdf` 붙여 열고 인쇄 → PDF 저장
- 또는 `quarto render slides/week01-slides.qmd --to pptx` (파워포인트, 스타일은 단순화됨)

## 스타일 요소(클래스) 사용법
본문 마크다운에서 아래처럼 씁니다.

| 쓰기 | 결과 |
|---|---|
| `[핵심]{.imp}` | 브랜드색(#1AB18B) 굵게 |
| `[키워드]{.red}` | 빨강 강조(핵심) |
| `[부연]{.grn}` | 초록(부연 설명) |
| `[why?]{.amb}` | 주황(주의/의문) |
| `[conv]{.navy}` | 네이비(영어 용어) |
| `[강아지]{.pill}` | 핑크 알약 라벨 (`.pill.teal`/`.navy`/`.amber`도 가능) |
| `[→]{.arrow}` | 굵은 회색 화살표 |
| `::: {.callbox} … :::` | 컬러 테두리 콜아웃 (`.teal`/`.red` 변형) |
| `::: {.keyline} … :::` | 핵심 한 줄 강조 막대 |

## 새 주차 슬라이드 만들기
1. `week01-slides.qmd`를 `weekNN-slides.qmd`로 복사
2. `title`/`subtitle`을 그 주차로 변경
3. 해당 주차 `weekNN-theory.qmd`의 핵심 개념·그림·수식을 슬라이드로 옮김
   - 그림은 `![](../images/xxx.png)`로 참조(책 그림 재사용)
   - 한 슬라이드에 한 개념, 불릿은 3~5개, 강조 클래스로 핵심만 컬러

> 그림·수식·색 팔레트는 책과 완전히 공유됩니다(같은 `images/`, 같은 브랜드색).
