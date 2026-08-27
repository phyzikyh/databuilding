# -*- coding: utf-8 -*-
"""교재용 matplotlib 그림 생성 스크립트 (학술 교재풍).
실행: python make_figures.py  → images/*.png 생성
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

plt.rcParams.update({
    "font.family": "Malgun Gothic",
    "axes.unicode_minus": False,
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.edgecolor": "#333333",
    "axes.linewidth": 0.9,
    "figure.dpi": 150,
    "savefig.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
})

# dataviz 스킬로 검증된 색맹 안전 팔레트 (브랜드색 #1AB18B 중심)
#   validate_palette.js: CVD ΔE 11.4 / 정상시야 23.5 통과(막대는 직접 라벨로 대비 보완)
C = dict(
    brand="#1AB18B", blue="#3C6EB4", amber="#E4842B", red="#C0392B",
    gray="#8a8f98", lgray="#d9dde2", ink="#222222",
    # 기존 코드 호환용 별칭(모두 검증 팔레트로 매핑)
    navy="#3C6EB4", teal="#1AB18B", green="#1AB18B",
)
from matplotlib.colors import LinearSegmentedColormap
TEAL_CMAP = LinearSegmentedColormap.from_list("teal", ["#eafaf4", "#1AB18B", "#0d6e56"])

OUT = "images"
os.makedirs(OUT, exist_ok=True)
def save(fig, name):
    fig.savefig(os.path.join(OUT, name))
    plt.close(fig)
    print("saved", name)

# ------------------------------------------------------------------
# W1: 데이터 품질 오류의 1-10-100 비용
# ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(5.2, 3.0))
stages = ["입력 시\n수정(1)", "나중에\n수정(10)", "미수정 후\n수습(100)"]
vals = [1, 10, 100]
bars = ax.bar(stages, vals, color=[C["green"], C["amber"], C["red"]], width=0.6)
ax.set_yscale("log")
ax.set_ylabel("상대 비용 (로그 척도)")
ax.set_title("나쁜 데이터가 치르는 비용: 1-10-100 규칙")
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v*1.15, str(v), ha="center", fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
save(fig, "w1_cost.png")

# ------------------------------------------------------------------
# W2: 편향 표본 vs 대표 표본
# ------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.9), sharey=True)
cats = ["긍정", "부정", "중립"]
axes[0].bar(cats, [90, 6, 4], color=C["red"]); axes[0].set_title("편향 표본")
axes[1].bar(cats, [40, 38, 22], color=C["green"]); axes[1].set_title("대표 표본")
for ax in axes:
    ax.set_ylim(0, 100); ax.spines[["top", "right"]].set_visible(False)
axes[0].set_ylabel("비율(%)")
fig.suptitle("표본의 편향 여부가 모델을 좌우한다", y=1.03, fontsize=12)
save(fig, "w2_sampling.png")

# ------------------------------------------------------------------
# W5: 분포의 모양 (대칭 vs 오른쪽 치우침) + 평균/중앙값
# ------------------------------------------------------------------
rng = np.random.default_rng(0)
sym = rng.normal(50, 10, 4000)
skew = rng.gamma(2.0, 12, 4000)
fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.0))
for ax, data, title in [(axes[0], sym, "대칭 분포"), (axes[1], skew, "오른쪽으로 치우친 분포")]:
    ax.hist(data, bins=40, color=C["navy"], alpha=0.75, edgecolor="white", linewidth=0.3)
    m, md = np.mean(data), np.median(data)
    ax.axvline(m, color=C["red"], lw=1.8, label=f"평균 {m:.0f}")
    ax.axvline(md, color=C["green"], lw=1.8, ls="--", label=f"중앙값 {md:.0f}")
    ax.set_title(title); ax.legend(fontsize=8); ax.set_yticks([])
    ax.spines[["top", "right", "left"]].set_visible(False)
fig.suptitle("분포의 모양과 평균·중앙값의 차이", y=1.02, fontsize=12)
save(fig, "w5_distribution.png")

# W5: 상자그림(IQR)과 이상값
fig, ax = plt.subplots(figsize=(5.6, 2.6))
data = list(rng.normal(60, 8, 60)) + [110, 5]  # 이상값 2개
bp = ax.boxplot(data, orientation="horizontal", widths=0.5, patch_artist=True,
                flierprops=dict(marker="o", markerfacecolor=C["red"],
                                markeredgecolor=C["red"], markersize=6))
bp["boxes"][0].set(facecolor="#dfe6f2", edgecolor=C["navy"])
for k in ["whiskers", "caps", "medians"]:
    for e in bp[k]: e.set(color=C["navy"], linewidth=1.4)
q1, q3 = np.percentile(data, [25, 75]); iqr = q3 - q1
ax.annotate("Q1", (q1, 1.32), ha="center", color=C["navy"])
ax.annotate("Q3", (q3, 1.32), ha="center", color=C["navy"])
ax.annotate("이상값", (110, 1.18), ha="center", color=C["red"], fontsize=9)
ax.annotate(f"IQR = Q3 - Q1 = {iqr:.0f}", (np.median(data), 0.62), ha="center", fontsize=9)
ax.set_yticks([]); ax.set_xlabel("값")
ax.set_title("상자그림(box plot)과 IQR 이상값 규칙")
ax.spines[["top", "right", "left"]].set_visible(False)
save(fig, "w5_boxplot.png")

# ------------------------------------------------------------------
# W10: 바운딩 박스 좌표계 (x, y, w, h) — 좌상단 원점
# ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(4.8, 3.6))
ax.add_patch(Rectangle((0, 0), 10, 8, fill=False, edgecolor="#bbb"))
bx, by, bw, bh = 3, 2, 4, 3.5
ax.add_patch(Rectangle((bx, by), bw, bh, fill=False, edgecolor=C["red"], linewidth=2))
ax.plot(bx, by, "o", color=C["red"]); ax.text(bx-0.2, by-0.35, "(x, y)", color=C["red"], ha="right")
ax.plot(bx+bw, by+bh, "o", color=C["navy"]); ax.text(bx+bw+0.2, by+bh+0.15, "(x+w, y+h)", color=C["navy"])
ax.annotate("", (bx+bw, by-0.5), (bx, by-0.5), arrowprops=dict(arrowstyle="<->", color=C["teal"]))
ax.text(bx+bw/2, by-0.9, "w (너비)", ha="center", color=C["teal"])
ax.annotate("", (bx-0.5, by+bh), (bx-0.5, by), arrowprops=dict(arrowstyle="<->", color=C["teal"]))
ax.text(bx-0.75, by+bh/2, "h (높이)", va="center", ha="right", color=C["teal"], rotation=90)
ax.text(0.1, 8.3, "원점 (0,0) — 좌상단", color="#666", fontsize=9)
ax.set_xlim(-1.5, 11); ax.set_ylim(9, -1)  # y축 뒤집기(아래로 증가)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title("이미지 좌표계와 바운딩 박스 (x, y, w, h)")
save(fig, "w10_bbox.png")

# W10: IoU (교집합 / 합집합)
fig, ax = plt.subplots(figsize=(4.8, 3.2))
A = (1, 1, 4, 3); B = (3, 2, 4, 3)
ax.add_patch(Rectangle(A[:2], A[2], A[3], alpha=0.35, color=C["navy"], label="박스 A"))
ax.add_patch(Rectangle(B[:2], B[2], B[3], alpha=0.35, color=C["red"], label="박스 B"))
ix1, iy1 = max(A[0], B[0]), max(A[1], B[1])
ix2, iy2 = min(A[0]+A[2], B[0]+B[2]), min(A[1]+A[3], B[1]+B[3])
ax.add_patch(Rectangle((ix1, iy1), ix2-ix1, iy2-iy1, color=C["green"], alpha=0.6))
inter = (ix2-ix1)*(iy2-iy1); union = A[2]*A[3]+B[2]*B[3]-inter
ax.text(4, 6.2, f"IoU = 교집합/합집합 = {inter/union:.2f}", ha="center", fontsize=10, color=C["green"])
ax.legend(loc="lower right", fontsize=8)
ax.set_xlim(0, 8); ax.set_ylim(0, 7); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("두 박스의 겹침 지표 IoU")
save(fig, "w10_iou.png")

# W10 / W12: 클래스 불균형 분포
fig, ax = plt.subplots(figsize=(5.0, 2.9))
ax.bar(["정상", "이상(암 등)"], [9900, 100], color=[C["navy"], C["red"]], width=0.55)
ax.set_ylabel("건수"); ax.set_title("클래스 불균형: 다수 vs 소수 클래스")
for i, v in enumerate([9900, 100]):
    ax.text(i, v+150, f"{v:,}", ha="center", fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
save(fig, "w12_imbalance.png")

# ------------------------------------------------------------------
# W11: 시계열 이상 구간 라벨
# ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6.4, 2.8))
t = np.arange(0, 8)
usage = np.array([20, 22, 25, 90, 95, 93, 30, 24])
ax.plot(t, usage, "-o", color=C["navy"], lw=1.8)
ax.axvspan(3, 5, color=C["red"], alpha=0.15)
ax.text(4, 100, "이상 구간\n(10:03~10:05)", ha="center", color=C["red"], fontsize=9)
ax.set_xticks(t); ax.set_xticklabels([f"10:0{i}" for i in t], fontsize=8)
ax.set_ylabel("CPU 사용률(%)"); ax.set_title("시계열 이상 구간 라벨링")
ax.spines[["top", "right"]].set_visible(False)
save(fig, "w11_timeseries.png")

# ------------------------------------------------------------------
# W12: 집단별 편향(승인 비율)
# ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(4.6, 2.9))
ax.bar(["집단 A", "집단 B"], [0.83, 0.42], color=[C["navy"], C["amber"]], width=0.5)
ax.set_ylim(0, 1); ax.set_ylabel("‘승인’ 비율")
ax.set_title("민감 속성별 라벨 비율 비교(편향 점검)")
for i, v in enumerate([0.83, 0.42]):
    ax.text(i, v+0.03, f"{v:.2f}", ha="center", fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
save(fig, "w12_bias.png")

# ------------------------------------------------------------------
# W13: Min-Max vs 표준화
# ------------------------------------------------------------------
vals = np.array([20, 40, 60, 80, 100], dtype=float)
mm = (vals - vals.min()) / (vals.max() - vals.min())
z = (vals - vals.mean()) / vals.std()
fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.9))
axes[0].plot(vals, mm, "-o", color=C["navy"]); axes[0].set_title("Min-Max 정규화 (0~1)")
axes[0].set_xlabel("원래 값"); axes[0].set_ylabel("변환 값")
axes[1].plot(vals, z, "-o", color=C["red"]); axes[1].set_title("표준화 (평균0, 표준편차1)")
axes[1].set_xlabel("원래 값"); axes[1].axhline(0, color="#bbb", lw=0.8)
for ax in axes: ax.spines[["top", "right"]].set_visible(False)
fig.suptitle("두 가지 스케일링 방법", y=1.03, fontsize=12)
save(fig, "w13_scaling.png")

# W13: 학습/검증/평가 분할
fig, ax = plt.subplots(figsize=(6.2, 1.5))
parts = [("학습셋 (65%)", 65, C["navy"]), ("검증셋 (15%)", 15, C["amber"]), ("평가셋 (20%)", 20, C["red"])]
left = 0
for name, w, col in parts:
    ax.barh(0, w, left=left, color=col, edgecolor="white")
    ax.text(left + w/2, 0, name, ha="center", va="center", color="white", fontsize=9, fontweight="bold")
    left += w
ax.set_xlim(0, 100); ax.axis("off")
ax.set_title("데이터 분할: 평가셋은 학습에 쓰지 않는다", fontsize=11)
save(fig, "w13_split.png")

# ------------------------------------------------------------------
# W14: 혼동 행렬 히트맵
# ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(4.2, 3.6))
cm = np.array([[40, 10], [8, 42]])  # [[TP,FN],[FP,TN]]
im = ax.imshow(cm, cmap=TEAL_CMAP)
labels = [["TP", "FN"], ["FP", "TN"]]
for i in range(2):
    for j in range(2):
        ax.text(j, i, f"{labels[i][j]}\n{cm[i,j]}", ha="center", va="center",
                color="white" if cm[i, j] > 25 else "#222", fontsize=11, fontweight="bold")
ax.set_xticks([0, 1]); ax.set_xticklabels(["예측=양성", "예측=음성"])
ax.set_yticks([0, 1]); ax.set_yticklabels(["실제=양성", "실제=음성"])
ax.set_title("혼동 행렬 (Confusion Matrix)")
save(fig, "w14_confusion.png")

# W14: 정밀도-재현율 트레이드오프
fig, ax = plt.subplots(figsize=(4.8, 3.2))
r = np.linspace(0.05, 1, 100)
p = np.clip(1.02 - 0.6 * r**1.7, 0, 1)
ax.plot(r, p, color=C["navy"], lw=2)
ax.set_xlabel("재현율(Recall)"); ax.set_ylabel("정밀도(Precision)")
ax.set_title("정밀도-재현율 트레이드오프")
ax.set_xlim(0, 1); ax.set_ylim(0, 1.05)
ax.spines[["top", "right"]].set_visible(False)
ax.annotate("보수적 예측", (0.15, 0.92), fontsize=8, color="#555")
ax.annotate("적극적 예측", (0.78, 0.35), fontsize=8, color="#555")
save(fig, "w14_pr.png")

# W14: 과적합 곡선
fig, ax = plt.subplots(figsize=(5.0, 3.1))
c = np.linspace(1, 10, 100)
train = 0.9 * np.exp(-0.35 * c) + 0.02
val = 0.9 * np.exp(-0.35 * c) + 0.02 + 0.02 * (c - 3)**2 * (c > 3)
ax.plot(c, train, color=C["navy"], lw=2, label="학습 오차")
ax.plot(c, val, color=C["red"], lw=2, label="평가 오차")
opt = c[np.argmin(val)]
ax.axvline(opt, color="#999", ls="--", lw=1)
ax.text(opt+0.1, 0.5, "적정 지점", fontsize=8, color="#555")
ax.text(8.2, 0.7, "과적합", fontsize=9, color=C["red"])
ax.set_xlabel("모델 복잡도 →"); ax.set_ylabel("오차"); ax.set_yticks([])
ax.set_title("과적합: 학습 오차 vs 평가 오차")
ax.legend(fontsize=8); ax.spines[["top", "right"]].set_visible(False)
save(fig, "w14_overfit.png")

# ------------------------------------------------------------------
# W15: K-겹 교차 검증
# ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6.2, 3.0))
K = 5
for i in range(K):
    for j in range(K):
        col = C["red"] if j == i else C["navy"]
        alpha = 0.85 if j == i else 0.35
        ax.add_patch(Rectangle((j, K-1-i), 0.94, 0.9, color=col, alpha=alpha))
    ax.text(-0.3, K-1-i+0.45, f"{i+1}회", ha="right", va="center", fontsize=9)
ax.add_patch(Rectangle((6.2, 3.2), 0.3, 0.3, color=C["red"], alpha=0.85)); ax.text(6.6, 3.35, "평가 조각", va="center", fontsize=9)
ax.add_patch(Rectangle((6.2, 2.5), 0.3, 0.3, color=C["navy"], alpha=0.35)); ax.text(6.6, 2.65, "학습 조각", va="center", fontsize=9)
ax.set_xlim(-1, 8.5); ax.set_ylim(-0.3, 5.2); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("5-겹 교차 검증: 조각을 번갈아 평가에 사용")
save(fig, "w15_cv.png")

# W15: 실험 비교
fig, ax = plt.subplots(figsize=(4.8, 2.9))
ax.bar(["LogReg", "DecisionTree", "개선 데이터\n+LogReg"], [0.72, 0.70, 0.81],
       color=[C["gray"], C["gray"], C["green"]], width=0.55)
ax.set_ylim(0, 1); ax.set_ylabel("교차검증 정확도")
ax.set_title("실험 비교: 모델보다 데이터 개선의 효과")
for i, v in enumerate([0.72, 0.70, 0.81]):
    ax.text(i, v+0.02, f"{v:.2f}", ha="center", fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
save(fig, "w15_experiments.png")

# ==================================================================
# 모델 아키텍처 그림
# ==================================================================
from matplotlib.patches import Circle, FancyBboxPatch

# W9: 지도학습 도식 (학습 / 예측)
fig, ax = plt.subplots(figsize=(6.6, 3.2))
def box(x, y, w, h, text, fc, tc="white", fs=10):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec="none"))
    ax.text(x+w/2, y+h/2, text, ha="center", va="center", color=tc, fontsize=fs, fontweight="bold")
def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=13, color=C["ink"], lw=1.3))
# 학습 단계
ax.text(-0.2, 2.55, "학습", fontsize=11, fontweight="bold", color=C["brand"])
box(0.2, 2.0, 1.7, 0.9, "특성 X\n+ 정답 y", C["blue"])
arrow(1.9, 2.45, 2.7, 2.45)
box(2.7, 2.0, 1.7, 0.9, "모델 학습\n(fit)", C["brand"])
arrow(4.4, 2.45, 5.2, 2.45)
box(5.2, 2.0, 1.7, 0.9, "학습된 모델", C["ink"])
# 예측 단계
ax.text(-0.2, 0.95, "예측", fontsize=11, fontweight="bold", color=C["amber"])
box(0.2, 0.4, 1.7, 0.9, "새 특성 X", C["blue"])
arrow(1.9, 0.85, 2.7, 0.85)
box(2.7, 0.4, 1.7, 0.9, "학습된 모델\n(predict)", C["ink"])
arrow(4.4, 0.85, 5.2, 0.85)
box(5.2, 0.4, 1.7, 0.9, "예측 결과", C["amber"])
ax.set_xlim(-0.6, 7.2); ax.set_ylim(0.1, 3.2); ax.axis("off")
ax.set_title("지도학습의 구조: 학습으로 규칙을 배우고 예측에 사용")
save(fig, "w9_supervised.png")

# W14: 로지스틱 회귀 아키텍처
fig, ax = plt.subplots(figsize=(6.8, 3.4))
inx = 0.6
ys = [2.7, 1.9, 1.1]
for i, y in enumerate(ys):
    ax.add_patch(Circle((inx, y), 0.28, fc=C["blue"], ec="none"))
    ax.text(inx, y, f"$x_{i+1}$", ha="center", va="center", color="white", fontsize=11)
# 가중합 노드
sx, sy = 3.2, 1.9
ax.add_patch(Circle((sx, sy), 0.42, fc=C["gray"], ec="none"))
ax.text(sx, sy, r"$\Sigma$", ha="center", va="center", color="white", fontsize=15)
for i, y in enumerate(ys):
    ax.add_patch(FancyArrowPatch((inx+0.28, y), (sx-0.42, sy), arrowstyle="-|>",
                                 mutation_scale=11, color=C["ink"], lw=1.1))
    ax.text((inx+sx)/2-0.1, (y+sy)/2+0.08, f"$w_{i+1}$", fontsize=9, color=C["ink"])
ax.text(sx, sy-0.72, "+ b (편향)", ha="center", fontsize=9, color=C["ink"])
# 시그모이드 박스
gx = 4.9
ax.add_patch(FancyBboxPatch((gx, sy-0.42), 1.0, 0.84, boxstyle="round,pad=0.02,rounding_size=0.1",
                            fc=C["brand"], ec="none"))
ax.text(gx+0.5, sy, r"$\sigma$", ha="center", va="center", color="white", fontsize=15)
ax.add_patch(FancyArrowPatch((sx+0.42, sy), (gx, sy), arrowstyle="-|>", mutation_scale=12, color=C["ink"], lw=1.2))
ax.text((sx+gx)/2+0.15, sy+0.18, "z", fontsize=10)
# 출력
ax.add_patch(FancyArrowPatch((gx+1.0, sy), (6.6, sy), arrowstyle="-|>", mutation_scale=12, color=C["ink"], lw=1.2))
ax.text(6.7, sy, "확률 p\n→ 클래스", va="center", fontsize=10, color=C["ink"])
ax.text(3.7, 0.15, r"$z = w_1 x_1 + w_2 x_2 + \cdots + b,\quad p = \sigma(z)$", ha="center", fontsize=11)
ax.set_xlim(0, 8.2); ax.set_ylim(-0.1, 3.4); ax.axis("off")
ax.set_title("로지스틱 회귀의 구조")
save(fig, "w14_logreg.png")

# W14: 시그모이드 함수
fig, ax = plt.subplots(figsize=(5.0, 3.0))
z = np.linspace(-8, 8, 200)
ax.plot(z, 1/(1+np.exp(-z)), color=C["brand"], lw=2.4)
ax.axhline(0.5, color=C["red"], ls="--", lw=1.2); ax.axvline(0, color="#ccc", lw=0.8)
ax.text(-7.5, 0.55, "0.5 임계값", color=C["red"], fontsize=9)
ax.text(3.5, 0.2, r"$\sigma(z)=\dfrac{1}{1+e^{-z}}$", fontsize=12)
ax.set_xlabel("z (가중합)"); ax.set_ylabel("확률 σ(z)")
ax.set_title("시그모이드 함수: 실수 z를 0~1 확률로 변환")
ax.spines[["top", "right"]].set_visible(False)
save(fig, "w14_sigmoid.png")

# W14: 의사결정나무 아키텍처
fig, ax = plt.subplots(figsize=(6.2, 3.6))
def node(x, y, text, fc, w=1.7, h=0.7, tc="white"):
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec="none"))
    ax.text(x, y, text, ha="center", va="center", color=tc, fontsize=9.5, fontweight="bold")
def edge(x1, y1, x2, y2, label):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11, color=C["ink"], lw=1.1))
    ax.text((x1+x2)/2+(0.15 if x2>x1 else -0.15), (y1+y2)/2+0.05, label, fontsize=9, color=C["ink"],
            ha="left" if x2 > x1 else "right")
node(3, 3, "평균점수 > 60 ?", C["gray"], w=2.2)
edge(2.4, 2.7, 1.3, 2.05, "아니오"); edge(3.6, 2.7, 4.7, 2.05, "예")
node(1.2, 1.7, "공부시간 > 6 ?", C["gray"], w=2.0)
node(4.8, 1.7, "합격", C["brand"], w=1.3)
edge(0.7, 1.4, 0.3, 0.75, "아니오"); edge(1.7, 1.4, 2.1, 0.75, "예")
node(0.3, 0.4, "불합격", C["red"], w=1.3)
node(2.1, 0.4, "합격", C["brand"], w=1.3)
ax.set_xlim(-0.6, 6.0); ax.set_ylim(-0.1, 3.6); ax.axis("off")
ax.set_title("의사결정나무의 구조: 질문을 따라 잎(예측)에 도달")
save(fig, "w14_tree.png")

print("\n총 생성 완료. images/ 폴더 확인.")
