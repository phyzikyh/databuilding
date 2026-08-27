# 데이터구축실습 (Quarto Book)

인공지능 학습을 위한 데이터 수집·구축 15주 교재입니다. Python + SQLite3 기반.

> **이 폴더(`databuilding`)가 단일 배포 소스입니다.** 학생용(정답 숨김·인터랙티브 퀴즈) 형식으로 통일했습니다.
> - **연습문제**: 선택지를 클릭하면 정답(✓)·오답(✗)이 표시됩니다. 정답은 화면에 미리 노출되지 않으며, 자세한 해설은 접이식 "노트"에서 확인합니다. (구현: `interactive.html` + `styles.scss`의 `.quiz-opt`)
> - `main` 브랜치에 push하면 `.github/workflows/publish.yml`이 자동으로 렌더 후 GitHub Pages에 배포합니다.
> - 그림(`images/*.png`)은 커밋된 파일을 그대로 사용합니다(리눅스 러너엔 한글 폰트가 없어 재생성하지 않음). 그림을 바꾸면 로컬에서 `python make_figures.py` 실행 후 PNG까지 커밋하세요.

## 구성

각 주차는 **이론 / 연습문제 / 코딩실습** 세 파일로 분리되어 있습니다.

- `_quarto.yml` — 책 설정 (1~15주차, 주차별 3파일)
- `index.qmd` — 서문 / 책 사용법
- `weekNN-theory.qmd` — 주차별 **이론** (개념 + Mermaid 그림 + 참고문헌 20편↑, 한글 8,000자 이상)
- `weekNN-quiz.qmd` — 주차별 **연습문제** (4지선다 20문항 + 정답·해설)
- `weekNN-lab.qmd` — 주차별 **코딩실습** (예제 코드 30분 + 학생 실습 과제 30분)
- `references.qmd` / `references.bib` — 참고문헌
- `styles.scss` — 한글 웹 스타일

## 렌더링 방법

Quarto가 필요합니다: <https://quarto.org/docs/download/>

```bash
# 실습 코드 실행에 쓰이는 파이썬 패키지(선택)
pip install pandas matplotlib scikit-learn beautifulsoup4

# HTML 책 빌드
quarto render

# 로컬 미리보기(자동 새로고침)
quarto preview
```

빌드 결과는 `_book/` 폴더에 생성됩니다(`_book/index.html`).

## 그림(matplotlib PNG)과 수식

MIT Vision Book / PRML 웹교재 스타일을 따릅니다.

- **그림(20개)**: `make_figures.py`가 matplotlib로 학술풍 PNG를 `images/`에 생성합니다. 다시 만들려면:
  ```bash
  python make_figures.py
  ```
  본문에서는 `![캡션](images/xxx.png){#fig-xxx}`로 삽입되고 `@fig-xxx`로 참조하면 **그림 5.1**처럼 자동 번호가 매겨집니다.
  - **모델 아키텍처 그림**: 로지스틱 회귀(뉴런 구조)·시그모이드·의사결정나무·지도학습 도식 포함(14·9주차).
  - **색 팔레트**: `dataviz` 스킬의 `validate_palette.js`로 **색맹 안전성 검증**을 통과한 브랜드 팔레트(#1AB18B 중심)를 사용합니다.
- **강조 요소(styles.scss)**:
  - `[중요 용어]{.imp}` → **#1AB18B** 색 강조
  - `::: {.keybox}` … `:::` → 핵심 메시지 강조 박스
  - `::: {.eqnote}` … `:::` → 수식 바로 아래 **기호 설명** 목록
- **수식**: MathJax로 렌더링됩니다(`$...$`, `$$...$$`). IQR·IoU·코헨 카파·Min-Max/Z-점수·정밀도/재현율/F1 등 핵심 공식은 번호가 붙는 디스플레이 수식(`{#eq-xxx}`)으로 제공되며 `@eq-xxx`로 참조합니다.
- **테마**: `styles.scss`가 정갈한 학술 교재풍(번호형 그림 캡션, booktabs식 표, 여백 중심 타이포, 진홍 강조)을 적용합니다.
- **자동 번호**: `_quarto.yml`의 `crossref` 설정으로 그림·표·식·절이 한글 접두어("그림", "표", "식")로 번호가 매겨집니다.

## 설계 원칙

- **이론/연습문제/코딩실습 분리**: 세 요소가 각각 별도의 장(페이지)으로 나뉘어 있습니다.
- **이론 8,000자 이상**: 각 이론 장의 본문(참고문헌 제외)은 한글 8,000자 이상입니다.
- **다이어그램 소스 비노출**: `_quarto.yml`에 `execute: echo: false`를 설정해, Mermaid 다이어그램의 소스 코드가 노출되지 않고 그림만 렌더링됩니다.
- **혼합 그림**: 데이터·기하·플롯 성격의 개념(분포·상자그림·바운딩박스·IoU·혼동행렬·교차검증 등)은 matplotlib PNG로, 구조·흐름(파이프라인·ER·프로세스)은 Mermaid로 표현합니다.
- **코드 블록**: 학습용 코드는 ```` ```python ```` 펜스로 표기되어 렌더 시 자동 실행되지 않습니다. 학생이 직접 복사해 실행합니다.
- **근거 자료**: 주차별 커리큘럼은 `데이터구축실습_강의계획서.pdf`를, 품질 개념은 `강의참고자료/`의 NIA 가이드라인(v4.0)을 근거로 작성했습니다.
