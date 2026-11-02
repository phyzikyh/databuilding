# -*- coding: utf-8 -*-
"""11주차 이론 그림(벡터 SVG) 생성 스크립트.

실행: python make_figures_w11.py [--preview <폴더>] [그림이름 ...]
  → images/w11_*.svg 생성. 캔버스 도구와 레이아웃 검사는 make_figures_w9.py의 Canvas를 쓴다.
색의 뜻: 파랑=입력, 청록=처리·층, 앰버=출력·정답·강조, 회색=보조.
"""
import os
import sys
import math
import numpy as np
import matplotlib.patches as mp

from make_figures_w9 import (Canvas, INK, MUTED, LINE, BRAND, BRAND_D, BRAND_L, BLUE, BLUE_D, BLUE_L,
                             AMBER, AMBER_D, AMBER_L, WHITE, GRAY_L, TITLE, BODY, SMALL, CHIP)

RNG = np.random.default_rng(7)


def arrow(c, pts, color=MUTED, lw=1.3, ls="-", head=10):
    c.line(pts, color, lw, ls=ls, head=head)


def circle(c, x, y, r, fc=WHITE, ec=LINE, lw=1.0, z=3):
    c.ax.add_patch(mp.Circle((x, y), r, fc=fc, ec=ec, lw=lw, zorder=z))


def vdots(c, x, y, col=MUTED):
    for dy in (-6, 0, 6):
        c.ax.add_patch(mp.Circle((x, y + dy), 1.6, fc=col, ec="none", zorder=4))


def panel_title(c, x, y, s):
    c.text(x, y, s, TITLE, 600, INK, ha="left")


# ═════════════════════ 반복 학습 프로세스 ═════════════════════
def fig_process():
    c = Canvas("w11_process", 560, 330)
    w, h, y0 = 122, 44, 14
    xs = [12, 152, 292, 426]
    top = [("문제 정의", "예측 대상·시점·지표"), ("EDA", "구조·분포·관계"), ("데이터 분할", "학습·검증·테스트"),
           ("베이스라인", "단순 기준 모델")]
    for (t, s), x in zip(top, xs):
        c.box_text((x, y0, w, h), t, s, BRAND_L, BRAND)
    for i in range(3):
        arrow(c, [(xs[i] + w, y0 + h / 2), (xs[i + 1], y0 + h / 2)])

    # 반복 개선 루프
    g = c.rect(150, 92, 400, 150, WHITE, AMBER, lw=1.3, r=8, ls=(0, (5, 3)), name="루프")
    c.text(162, 104, "검증 데이터로 반복", SMALL, 700, AMBER_D, ha="left", owner=g)
    bw, bh = 150, 42
    A = (382, 116, bw, bh)    # 오른쪽 위
    B = (382, 188, bw, bh)    # 오른쪽 아래
    C_ = (168, 188, bw, bh)   # 왼쪽 아래
    D = (168, 116, bw, bh)    # 왼쪽 위
    for bx, t in ((A, "예측·오류 분석"), (B, "특성·데이터 개선"), (C_, "하이퍼파라미터 탐색"), (D, "교차검증·비교")):
        b = c.rect(*bx, WHITE, AMBER, lw=1.2, r=5, name=t, parent=g)
        c.text(bx[0] + bw / 2, bx[1] + bh / 2, t, BODY, 600, INK, owner=b)
    arrow(c, [(A[0] + bw / 2, A[1] + bh), (B[0] + bw / 2, B[1])], AMBER_D)
    arrow(c, [(B[0], B[1] + bh / 2), (C_[0] + bw, C_[1] + bh / 2)], AMBER_D)
    arrow(c, [(C_[0] + bw / 2, C_[1]), (D[0] + bw / 2, D[1] + bh)], AMBER_D)
    arrow(c, [(D[0] + bw, D[1] + bh / 2), (A[0], A[1] + bh / 2)], AMBER_D)
    # 진입: 베이스라인 → 루프
    arrow(c, [(xs[3] + w / 2, y0 + h), (xs[3] + w / 2, 92)])

    # 아래 줄: 확정 → 테스트 → 운영
    yb = 276
    bot = [("최종 모델 확정", "검증 결과로 선택"), ("테스트 평가", "한 번만 사용"), ("예측·모니터링", "새 데이터에 적용")]
    xb = [12, 200, 388]
    for (t, s), x in zip(bot, xb):
        c.box_text((x, yb, 160, h), t, s, BLUE_L, BLUE, tcolor=BLUE_D)
    # 루프 → 확정: 왼쪽 아래 상자에서 빠져나감
    arrow(c, [(150, C_[1] + bh / 2), (92, C_[1] + bh / 2), (92, yb)])
    c.text(88, C_[1] + bh / 2 - 12, "개선이 멈추면", SMALL, 500, MUTED, ha="right")
    arrow(c, [(172, yb + h / 2), (200, yb + h / 2)])
    arrow(c, [(360, yb + h / 2), (388, yb + h / 2)])
    return c


# ═════════════════════ 데이터 분할 ═════════════════════
def bar(c, x, y, w, h, fc, ec, label=None, tc=INK, name=None, size=SMALL):
    b = c.rect(x, y, w, h, fc, ec, lw=0.9, r=0, name=name or f"bar{x:.0f},{y:.0f}", parent="bars")
    if label:
        c.text(x + w / 2, y + h / 2, label, size, 600, tc, owner=b)
    return b


def fig_split():
    c = Canvas("w11_split", 560, 332)
    X0, W = 120, 428
    # (a) 홀드아웃
    panel_title(c, 12, 14, "(a) 홀드아웃")
    y = 32
    bar(c, X0, y, W * 0.6, 24, BLUE_L, BLUE, "학습 60%", BLUE_D, name="a1")
    bar(c, X0 + W * 0.6, y, W * 0.2, 24, AMBER_L, AMBER, "검증 20%", AMBER_D, name="a2")
    bar(c, X0 + W * 0.8, y, W * 0.2, 24, GRAY_L, MUTED, "테스트 20%", INK, name="a3")
    c.text(X0 - 10, y + 12, "한 번 나누기", SMALL, 500, MUTED, ha="right")

    # (b) K-겹 교차검증
    panel_title(c, 12, 80, "(b) 5-겹 교차검증")
    yk, rh = 98, 20
    tw = W * 0.8
    seg = tw / 5
    for k in range(5):
        yy = yk + k * (rh + 5)
        c.text(X0 - 10, yy + rh / 2, f"반복 {k + 1}", SMALL, 500, MUTED, ha="right")
        for j in range(5):
            val = j == k
            bar(c, X0 + j * seg, yy, seg, rh, AMBER_L if val else BLUE_L, AMBER if val else BLUE,
                "검증" if val else "학습", AMBER_D if val else BLUE_D, name=f"k{k}{j}")
    bar(c, X0 + tw + 8, yk, W - tw - 8, 5 * rh + 20, GRAY_L, MUTED, "테스트", INK, name="ktest")
    c.text(X0 + tw / 2, yk + 5 * (rh + 5) + 8, "다섯 검증 점수의 평균과 흩어짐으로 비교", SMALL, 400, MUTED)

    # (c) 시간 순서 분할
    panel_title(c, 12, 242, "(c) 시간 순서 분할")
    yt = 258
    for k in range(2):
        yy = yt + k * 26
        tr = W * (0.45 + 0.2 * k)
        bar(c, X0, yy, tr, 20, BLUE_L, BLUE, "과거: 학습", BLUE_D, name=f"t{k}a")
        bar(c, X0 + tr, yy, W * 0.15, 20, AMBER_L, AMBER, "이후: 검증", AMBER_D, name=f"t{k}b")
        c.text(X0 - 10, yy + 10, f"분할 {k + 1}", SMALL, 500, MUTED, ha="right")
    c.text(X0 + W, yt + 62, "시간 →", SMALL, 600, MUTED, ha="right")
    return c


# ═════════════════════ 과소적합·적절·과적합 ═════════════════════
def fig_fit():
    c = Canvas("w11_fit", 560, 200)
    x = np.linspace(0.04, 0.96, 12) + RNG.uniform(-0.025, 0.025, 12)
    y = np.sin(2 * np.pi * x) + RNG.normal(0, 0.18, x.size)
    grid = np.linspace(0, 1, 300)
    titles = (("과소적합", "직선이라 굽은 관계를 못 따라감"), ("적절한 적합", "전체 경향을 따라감"),
              ("과적합", "학습 점을 외워 새 데이터에 약함"))
    for i, deg in enumerate((1, 3, 11)):
        px, py, pw, ph = 12 + 184 * i, 14, 168, 120
        frame = c.rect(px, py, pw, ph, WHITE, LINE, lw=1.0, r=4, name=f"fit{i}")

        def tx(v):
            return px + 10 + v * (pw - 20)

        def ty(v):
            return py + ph / 2 - v * (ph / 2 - 12) / 1.5

        coef = np.polyfit(x, y, deg)
        fy = np.polyval(coef, grid)
        fy = np.where(np.abs(fy) > 1.55, np.nan, fy)      # 틀 밖으로 나가는 부분은 그리지 않음
        c.ax.plot([tx(v) for v in grid], [ty(v) for v in fy], color=AMBER, lw=1.8, zorder=3)
        c.ax.scatter([tx(v) for v in x], [ty(v) for v in y], s=16, color=BLUE, zorder=4, edgecolors=WHITE,
                     linewidths=0.6)
        c.text(px + pw / 2, py + ph + 16, titles[i][0], BODY, 700, INK)
        c.text(px + pw / 2, py + ph + 34, titles[i][1], SMALL, 400, MUTED)
    return c


# ═════════════════════ 선형회귀·로지스틱 회귀 ═════════════════════
def neuron_row(c, y0, title, out_parts):
    panel_title(c, 12, y0, title)
    ys = [y0 + 26, y0 + 56, y0 + 104]
    labels = [r"$x_1$", r"$x_2$", r"$x_p$"]
    for yy, lb in zip(ys, labels):
        circle(c, 60, yy, 13, BLUE_L, BLUE, 1.2)
        c.text(60, yy, lb, BODY, 600, BLUE_D)
    vdots(c, 60, y0 + 81)
    sx, sy = 190, y0 + 65
    circle(c, sx, sy, 22, BRAND_L, BRAND, 1.4)
    c.text(sx, sy, "Σ", TITLE + 3, 700, BRAND_D)
    for yy, wl in zip(ys, (r"$w_1$", r"$w_2$", r"$w_p$")):
        dx, dy = sx - 73, sy - yy
        L = math.hypot(dx, dy)
        x1, y1 = sx - 22 * dx / L, sy - 22 * dy / L
        c.ax.annotate("", xy=(x1, y1), xytext=(73, yy), zorder=2,
                      arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.1, mutation_scale=9, shrinkA=0, shrinkB=0))
        c.text((73 + x1) / 2, (yy + y1) / 2 - 9, wl, SMALL, 600, MUTED)
    c.text(sx, sy + 34, r"$+\ b$", SMALL, 600, BRAND_D)
    x = sx + 22
    for kind, a, b_ in out_parts:
        if kind == "arrow":
            arrow(c, [(x, sy), (x + a, sy)])
            if b_:
                c.text(x + a / 2, sy - 11, b_, SMALL, 600, MUTED)
            x += a
        elif kind == "box":
            bb = c.rect(x, sy - 22, a, 44, b_[1], b_[2], lw=1.3, r=5, name=b_[0] + str(y0))
            c.text(x + a / 2, sy - 7, b_[0], BODY, 700, b_[3], owner=bb)
            c.text(x + a / 2, sy + 10, b_[4], SMALL, 400, MUTED, owner=bb)
            x += a
    return sy


def fig_linear():
    c = Canvas("w11_linear", 560, 290)
    neuron_row(c, 14, "(a) 선형회귀", [
        ("arrow", 60, r"$z$"),
        ("box", 150, (r"예측값  $\hat{y} = z$", AMBER_L, AMBER, AMBER_D, "수치를 그대로 출력")),
    ])
    sy = neuron_row(c, 152, "(b) 로지스틱 회귀", [
        ("arrow", 26, r"$z$"),
        ("box", 90, ("시그모이드", BRAND_L, BRAND, BRAND_D, "0~1로 변환")),
        ("arrow", 24, None),
        ("box", 90, ("확률  p", AMBER_L, AMBER, AMBER_D, "P(y=1 | x)")),
        ("arrow", 24, None),
        ("box", 84, ("클래스", WHITE, INK, INK, "p ≥ 0.5 → 1")),
    ])
    return c


# ═════════════════════ SVM ═════════════════════
def fig_svm():
    c = Canvas("w11_svm", 560, 244)
    # (a) 선형 SVM
    panel_title(c, 12, 14, "(a) 마진을 최대로 하는 경계")
    px, py, pw, ph = 12, 30, 256, 180
    c.rect(px, py, pw, ph, WHITE, LINE, lw=1.0, r=4, name="svmA")

    def T(u, v):          # 0~1 좌표 → 캔버스
        return px + 12 + u * (pw - 24), py + ph - 12 - v * (ph - 24)

    a_pts = np.array([[0.12, 0.62], [0.2, 0.82], [0.08, 0.38], [0.28, 0.6], [0.3, 0.9], [0.18, 0.5], [0.36, 0.75]])
    b_pts = np.array([[0.7, 0.3], [0.82, 0.5], [0.9, 0.2], [0.62, 0.12], [0.78, 0.1], [0.92, 0.42], [0.66, 0.42]])
    # 경계: v = u - 0.0 + 0.2 꼴, 직선 u - v = c
    for off, ls, col in ((0.0, "-", INK), (0.18, (0, (4, 3)), MUTED), (-0.18, (0, (4, 3)), MUTED)):
        u0, u1 = max(0.0, -off), min(1.0, 1.0 - off)      # v = u + off 가 0~1 안에 있는 구간
        (x0, y0), (x1, y1) = T(u0, u0 + off), T(u1, u1 + off)
        c.ax.plot([x0, x1], [y0, y1], color=col, lw=1.6 if ls == "-" else 1.1, ls=ls, zorder=2)
    for u, v in a_pts:
        x, y = T(u, v); circle(c, x, y, 5, BLUE, WHITE, 0.8, 4)
    for u, v in b_pts:
        x, y = T(u, v); circle(c, x, y, 5, AMBER, WHITE, 0.8, 4)
    # 서포트 벡터(점선 위의 점) 표시
    for u, v, col in ((0.36, 0.54, BLUE), (0.66, 0.48, AMBER), (0.55, 0.37, AMBER)):
        x, y = T(u, v); circle(c, x, y, 5, col, WHITE, 0.8, 4); circle(c, x, y, 9, "none", INK, 1.1, 5)
    # 범례(그림 아래)
    ly = py + ph + 18
    c.ax.plot([px + 4, px + 26], [ly, ly], color=INK, lw=1.6, zorder=3)
    c.text(px + 32, ly, "결정 경계", SMALL, 500, INK, ha="left")
    c.ax.plot([px + 92, px + 114], [ly, ly], color=MUTED, lw=1.1, ls=(0, (4, 3)), zorder=3)
    c.text(px + 120, ly, "마진 경계", SMALL, 500, INK, ha="left")
    circle(c, px + 186, ly, 7, "none", INK, 1.1, 5)
    c.text(px + 198, ly, "서포트 벡터", SMALL, 500, INK, ha="left")

    # (b) 커널
    panel_title(c, 292, 14, "(b) 커널로 만든 굽은 경계")
    qx, qy, qw, qh = 292, 30, 256, 180
    c.rect(qx, qy, qw, qh, WHITE, LINE, lw=1.0, r=4, name="svmB")
    cx, cy = qx + qw / 2, qy + qh / 2
    ang = RNG.uniform(0, 2 * np.pi, 22)
    for t in ang[:9]:
        r = RNG.uniform(0, 28)
        circle(c, cx + r * np.cos(t), cy + r * np.sin(t), 5, BLUE, WHITE, 0.8, 4)
    for t in ang[9:]:
        r = RNG.uniform(58, 76)
        circle(c, cx + r * np.cos(t), cy + r * np.sin(t) * 0.95, 5, AMBER, WHITE, 0.8, 4)
    c.ax.add_patch(mp.Ellipse((cx, cy), 2 * 44, 2 * 44, fc="none", ec=INK, lw=1.6, zorder=3))
    c.text(qx + qw / 2, qy + qh + 18, "직선으로는 못 나누는 데이터도 커널로 나눔", SMALL, 500, INK)
    return c


# ═════════════════════ k-NN ═════════════════════
def fig_knn():
    c = Canvas("w11_knn", 560, 228)
    px, py, pw, ph = 12, 14, 300, 186
    c.rect(px, py, pw, ph, WHITE, LINE, lw=1.0, r=4, name="knn")
    qx, qy = px + 150, py + 95
    blue = [(-30, -22), (24, -30), (-12, 34), (40, 52), (-70, -60), (-110, 10), (-90, 60), (60, -70)]
    amber = [(34, 14), (-38, 16), (90, 20), (110, -40), (80, 70), (120, 60), (-40, -75)]
    pts = [(dx, dy, BLUE) for dx, dy in blue] + [(dx, dy, AMBER) for dx, dy in amber]
    pts.sort(key=lambda p: math.hypot(p[0], p[1]))
    k = 5
    rad = (math.hypot(*pts[k - 1][:2]) + math.hypot(*pts[k][:2])) / 2
    c.ax.add_patch(mp.Circle((qx, qy), rad, fc=BRAND_L, ec=BRAND, lw=1.2, ls=(0, (4, 3)), zorder=2.5))
    for dx, dy, col in pts:
        circle(c, qx + dx, qy + dy, 5.5, col, WHITE, 0.8, 4)
    c.ax.plot([qx], [qy], marker="*", ms=15, color=INK, zorder=6, mec=WHITE, mew=0.8)
    nb = sum(1 for p in pts[:k] if p[2] == BLUE)
    c.text(px + pw / 2, py + ph + 15, "★ 새 데이터, 점선 원 = 가장 가까운 5개", SMALL, 600, BRAND_D)
    # 오른쪽 설명
    x = 340
    c.text(x, 40, "가까운 5개의 정답", BODY, 700, INK, ha="left")
    circle(c, x + 6, 66, 5.5, BLUE, WHITE, 0.8)
    c.text(x + 18, 66, f"파랑 {nb}개", BODY, 500, INK, ha="left")
    circle(c, x + 6, 90, 5.5, AMBER, WHITE, 0.8)
    c.text(x + 18, 90, f"주황 {k - nb}개", BODY, 500, INK, ha="left")
    b = c.rect(x, 112, 200, 34, AMBER_L, AMBER, lw=1.3, r=5, name="knn결과")
    c.text(x + 100, 129, "다수결 → " + ("파랑" if nb > k - nb else "주황"), BODY, 700, AMBER_D, owner=b)
    c.text(x, 166, "회귀라면 이웃 값의 평균을 예측", SMALL, 400, MUTED, ha="left")
    c.text(x, 184, "거리를 쓰므로 스케일링이 필요", SMALL, 400, MUTED, ha="left")
    return c


# ═════════════════════ 의사결정나무 ═════════════════════
def fig_tree():
    c = Canvas("w11_tree", 560, 250)
    def node(x, y, w, t, sub, fc, ec, tc):
        return c.box_text((x - w / 2, y, w, 44), t, sub, fc, ec, tcolor=tc)
    node(280, 14, 170, "주말인가?", "뿌리 노드", BRAND_L, BRAND, INK)
    node(140, 104, 170, "강수량 ≥ 5mm?", "내부 노드", BRAND_L, BRAND, INK)
    node(420, 104, 170, "출근 시간대?", "내부 노드", BRAND_L, BRAND, INK)
    leaves = [(70, "30대"), (210, "140대"), (350, "180대"), (490, "60대")]
    for x, v in leaves:
        node(x, 196, 112, f"예측 {v}", "잎 노드", AMBER_L, AMBER, AMBER_D)
    for (x0, x1, lab) in ((280, 140, "예"), (280, 420, "아니오")):
        arrow(c, [(x0, 58), (x0, 80), (x1, 80), (x1, 104)])
        c.text((x0 + x1) / 2, 71, lab, SMALL, 600, MUTED)
    for (x0, x1, lab) in ((140, 70, "예"), (140, 210, "아니오"), (420, 350, "예"), (420, 490, "아니오")):
        arrow(c, [(x0, 148), (x0, 172), (x1, 172), (x1, 196)])
        c.text((x0 + x1) / 2 + (-14 if x1 < x0 else 14), 163, lab, SMALL, 600, MUTED)
    return c


# ═════════════════════ 랜덤 포레스트 ═════════════════════
def mini_tree(c, x, y, s=1.0, col=BRAND):
    pts = [(x, y), (x - 14 * s, y + 16 * s), (x + 14 * s, y + 16 * s), (x - 22 * s, y + 32 * s), (x - 6 * s, y + 32 * s)]
    for a, b in ((0, 1), (0, 2), (1, 3), (1, 4)):
        c.ax.plot([pts[a][0], pts[b][0]], [pts[a][1], pts[b][1]], color=col, lw=1.1, zorder=3)
    for p in pts:
        circle(c, p[0], p[1], 3.6 * s, WHITE, col, 1.1, 4)


def fig_forest():
    c = Canvas("w11_forest", 560, 270)
    c.box_text((12, 100, 90, 50), "학습 데이터", "n개 행", BLUE_L, BLUE, tcolor=BLUE_D)
    ys = [16, 105, 196]
    names = ("표본 1", "표본 2", "표본 B")
    for i, yy in enumerate(ys):
        c.box_text((150, yy, 96, 40), names[i], "복원추출", BLUE_L, BLUE, tcolor=BLUE_D)
        arrow(c, [(102, 125), (126, 125), (126, yy + 20), (150, yy + 20)]) if i != 1 else arrow(c, [(102, 125), (150, 125)])
        b = c.rect(274, yy - 4, 92, 48, WHITE, BRAND, lw=1.2, r=5, name=f"tree{i}")
        mini_tree(c, 304, yy + 3)
        c.text(340, yy + 20, f"트리 {['1', '2', 'B'][i]}", SMALL, 600, BRAND_D, owner=b)
        arrow(c, [(246, yy + 20), (274, yy + 20)])
        arrow(c, [(366, yy + 20), (400, yy + 20), (400, 125), (414, 125)]) if i != 1 else arrow(c, [(366, 125), (414, 125)])
    vdots(c, 198, 172)
    vdots(c, 320, 172)
    c.box_text((414, 100, 134, 50), "평균·다수결", "회귀는 평균, 분류는 투표", AMBER_L, AMBER, tcolor=AMBER_D)
    c.text(280, 258, "각 분할에서 특성도 일부만 무작위로 골라 트리끼리 다르게 만듦", SMALL, 500, MUTED)
    return c


# ═════════════════════ 그래디언트 부스팅 ═════════════════════
def fig_boost():
    c = Canvas("w11_boost", 560, 236)
    xs = [12, 200, 388]
    for i, x in enumerate(xs):
        b = c.rect(x, 20, 160, 88, WHITE, BRAND, lw=1.2, r=6, name=f"m{i}")
        mini_tree(c, x + 30, 34)
        c.text(x + 100, 44, f"트리 {i + 1}", BODY, 700, BRAND_D, owner=b)
        c.text(x + 100, 64, ["정답 y를 학습", "남은 오차를 학습", "남은 오차를 학습"][i], SMALL, 500, INK, owner=b)
        c.text(x + 100, 84, [r"$f_1(x)$", r"$f_2(x)$", r"$f_3(x)$"][i], SMALL, 600, MUTED, owner=b)
        # 남은 오차 막대
        rem = [1.0, 0.55, 0.3, 0.16][i + 1]
        c.text(x + 10, 132, "남은 오차", SMALL, 500, MUTED, ha="left")
        c.rect(x + 64, 124, 96, 16, GRAY_L, LINE, lw=0.8, r=2, name=f"remb{i}")
        c.rect(x + 66, 124, 96 * rem, 16, AMBER_L, AMBER, lw=0.8, r=2, name=f"rem{i}", parent=None) if False else \
            c.ax.add_patch(mp.Rectangle((x + 64, 124), 96 * rem, 16, fc=AMBER, ec="none", alpha=0.55, zorder=3))
    for i in range(2):
        arrow(c, [(xs[i] + 160, 64), (xs[i + 1], 64)], AMBER_D)
        c.text((xs[i] + 160 + xs[i + 1]) / 2, 50, "오차", SMALL, 600, AMBER_D)
    b = c.rect(96, 168, 368, 50, AMBER_L, AMBER, lw=1.4, r=6, name="합")
    c.text(280, 185, r"최종 예측  $\hat{y} = f_1(x) + \eta\, f_2(x) + \eta\, f_3(x) + \cdots$", BODY, 600, AMBER_D, owner=b)
    c.text(280, 205, "η(학습률)가 작을수록 천천히, 더 많은 트리로 보완", SMALL, 400, MUTED, owner=b)
    return c


# ═════════════════════ k-평균·PCA ═════════════════════
def fig_unsup():
    c = Canvas("w11_unsup", 560, 230)
    panel_title(c, 12, 14, "(a) k-평균 군집 (k = 3)")
    px, py, pw, ph = 12, 30, 256, 186
    c.rect(px, py, pw, ph, WHITE, LINE, lw=1.0, r=4, name="km")
    centers = [(80, 80), (190, 90), (130, 170)]
    cols = [BLUE, AMBER, BRAND]
    for (cx, cy), col in zip(centers, cols):
        pts = RNG.normal(0, 14, (12, 2))
        for dx, dy in pts:
            circle(c, px + cx + dx, py + cy - 30 + dy, 4.5, col, WHITE, 0.7, 4)
        c.ax.plot([px + cx], [py + cy - 30], marker="X", ms=13, color=INK, mec=WHITE, mew=1.0, zorder=6)
    c.text(px + pw - 8, py + ph - 12, "X = 군집 중심", SMALL, 600, INK, ha="right")

    panel_title(c, 292, 14, "(b) 주성분 분석(PCA)")
    qx, qy, qw, qh = 292, 30, 256, 186
    c.rect(qx, qy, qw, qh, WHITE, LINE, lw=1.0, r=4, name="pca")
    cx, cy = qx + qw / 2, qy + qh / 2
    t = RNG.normal(0, 1, 50); s = RNG.normal(0, 0.28, 50)
    ang = math.radians(-28)
    for a, b in zip(t, s):
        x = cx + 46 * (a * math.cos(ang) - b * math.sin(ang))
        y = cy + 46 * (a * math.sin(ang) + b * math.cos(ang))
        circle(c, x, y, 3.8, BLUE_L, BLUE, 0.8, 3)
    for L, ang2, lab, col in ((92, ang, "PC1", AMBER_D), (34, ang + math.pi / 2, "PC2", BRAND_D)):
        ex, ey = cx + L * math.cos(ang2), cy + L * math.sin(ang2)
        c.ax.annotate("", xy=(ex, ey), xytext=(cx, cy), zorder=5,
                      arrowprops=dict(arrowstyle="-|>", color=col, lw=2.0, mutation_scale=12, shrinkA=0, shrinkB=0))
        c.text(ex + 6 * math.cos(ang2) + (10 if lab == "PC1" else 0), ey + 9 * math.sin(ang2) - (2 if lab == "PC1" else 4),
               lab, SMALL, 700, col)
    c.text(qx + qw - 8, qy + qh - 12, "분산이 큰 방향부터 새 축으로", SMALL, 500, MUTED, ha="right")
    return c


# ═════════════════════ 신경망 학습 순환 ═════════════════════
def fig_trainloop():
    c = Canvas("w11_trainloop", 560, 236)
    w, h = 150, 50
    P = {"in": (12, 20), "fw": (205, 20), "loss": (398, 20), "bw": (398, 156), "up": (205, 156)}
    c.box_text((*P["in"], w, h), "미니배치", "학습 데이터 일부", BLUE_L, BLUE, tcolor=BLUE_D)
    c.box_text((*P["fw"], w, h), "순전파", r"입력 → 예측값 $\hat{y}$", BRAND_L, BRAND)
    c.box_text((*P["loss"], w, h), "손실 계산", r"$L(y, \hat{y})$", AMBER_L, AMBER, tcolor=AMBER_D)
    c.box_text((*P["bw"], w, h), "역전파", "가중치별 기울기 ∂L/∂w", BRAND_L, BRAND)
    c.box_text((*P["up"], w, h), "가중치 갱신", "w ← w − η·∂L/∂w", BRAND_L, BRAND)
    arrow(c, [(162, 45), (205, 45)])
    arrow(c, [(355, 45), (398, 45)])
    arrow(c, [(473, 70), (473, 156)])
    arrow(c, [(398, 181), (355, 181)])
    arrow(c, [(280, 156), (280, 70)], AMBER_D)
    c.text(290, 113, "다음 미니배치로 반복", SMALL, 600, AMBER_D, ha="left")
    c.text(12, 120, "에포크: 학습 데이터 전체를", SMALL, 500, MUTED, ha="left")
    c.text(12, 136, "한 번 다 쓰는 단위", SMALL, 500, MUTED, ha="left")
    c.text(12, 168, "η: 학습률", SMALL, 500, MUTED, ha="left")
    c.text(12, 184, "옵티마이저: SGD, Adam 등", SMALL, 500, MUTED, ha="left")
    return c


# ═════════════════════ MLP ═════════════════════
def fig_mlp():
    c = Canvas("w11_mlp", 560, 262)
    layers = [4, 6, 6, 3]
    xs = [70, 210, 350, 490]
    cols = [(BLUE_L, BLUE), (BRAND_L, BRAND), (BRAND_L, BRAND), (AMBER_L, AMBER)]
    ytop, ybot = 24, 196
    pos = []
    for n, x in zip(layers, xs):
        gap = (ybot - ytop) / (max(layers) - 1)
        span = gap * (n - 1)
        y0 = (ytop + ybot) / 2 - span / 2
        pos.append([(x, y0 + gap * i) for i in range(n)])
    for a, b in zip(pos[:-1], pos[1:]):
        for (x0, y0) in a:
            for (x1, y1) in b:
                c.ax.plot([x0, x1], [y0, y1], color="#C9CFD8", lw=0.7, zorder=1)
    for ps, (fc, ec) in zip(pos, cols):
        for x, y in ps:
            circle(c, x, y, 11, fc, ec, 1.2, 3)
    labels = (("입력층", "특성 4개"), ("은닉층 1", "가중합 → ReLU"), ("은닉층 2", "가중합 → ReLU"),
              ("출력층", "softmax 또는 선형"))
    for x, (t, s) in zip(xs, labels):
        c.text(x, 222, t, BODY, 700, INK)
        c.text(x, 240, s, SMALL, 400, MUTED)
    return c


# ═════════════════════ 합성곱 연산 ═════════════════════
def fig_conv():
    c = Canvas("w11_conv", 560, 214)
    X = np.array([[1, 0, 1, 2, 0], [0, 2, 1, 0, 1], [1, 1, 0, 1, 2], [2, 0, 1, 1, 0], [0, 1, 2, 0, 1]])
    K = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]])
    out = np.array([[int((X[i:i + 3, j:j + 3] * K).sum()) for j in range(3)] for i in range(3)])
    s = 26

    def grid(x0, y0, M, name, fc, ec, hl=None, hlc=AMBER):
        n, m = M.shape
        for i in range(n):
            for j in range(m):
                on = hl is not None and hl[0] <= i < hl[0] + hl[2] and hl[1] <= j < hl[1] + hl[2]
                b = c.rect(x0 + j * s, y0 + i * s, s, s, AMBER_L if on else fc, ec, lw=0.8, r=0,
                           name=f"{name}{i}{j}", parent="g")
                c.text(x0 + j * s + s / 2, y0 + i * s + s / 2, str(M[i, j]), SMALL, 600, INK)
        if hl is not None:
            c.rect(x0 + hl[1] * s, y0 + hl[0] * s, hl[2] * s, hl[2] * s, "none", hlc, lw=2.2, r=0,
                   name=name + "hl", parent="g", z=5)

    panel_title(c, 12, 14, "입력 (5×5)")
    grid(12, 34, X, "x", BLUE_L, BLUE, hl=(0, 0, 3))
    c.text(222, 100, "*", TITLE + 6, 700, INK)
    panel_title(c, 246, 14, "필터 (3×3)")
    grid(246, 60, K, "k", BRAND_L, BRAND)
    c.text(343, 100, "=", TITLE + 4, 700, INK)
    panel_title(c, 366, 14, "특성 맵 (3×3)")
    grid(366, 60, out, "o", WHITE, MUTED, hl=(0, 0, 1))
    c.text(280, 192, f"강조한 3×3 칸과 필터를 칸끼리 곱해 더하면 {out[0, 0]}. 필터를 한 칸씩 옮기며 반복", SMALL, 500, MUTED)
    return c


# ═════════════════════ CNN 구조 ═════════════════════
def stack(c, x, y, w, h, n, fc, ec, d=4):
    for k in range(n - 1, -1, -1):
        c.ax.add_patch(mp.Rectangle((x + k * d, y - k * d), w, h, fc=fc, ec=ec, lw=0.9, zorder=3 + (n - k) * 0.01))


def fig_cnn():
    c = Canvas("w11_cnn", 560, 236)
    yb = 150    # 블록 아래 기준선
    items = [
        (12, 64, 3, BLUE_L, BLUE, "입력", "64×64×3"),
        (100, 64, 5, BRAND_L, BRAND, "합성곱+ReLU", "64×64×16"),
        (196, 40, 5, GRAY_L, MUTED, "풀링", "32×32×16"),
        (270, 40, 7, BRAND_L, BRAND, "합성곱+ReLU", "32×32×32"),
        (352, 24, 7, GRAY_L, MUTED, "풀링", "16×16×32"),
    ]
    for x, sz, n, fc, ec, t, sub in items:
        stack(c, x, yb - sz, sz, sz, n, fc, ec)
        cx = x + sz / 2 + (n - 1) * 2
        c.text(cx, yb + 18, t, SMALL, 700, INK)
        c.text(cx, yb + 34, sub, SMALL, 400, MUTED)
    for x0, x1 in ((88, 100), (182, 196), (256, 270), (336, 352)):
        arrow(c, [(x0, yb - 20), (x1, yb - 20)], head=8)
    # 평탄화 + 완전연결 + 출력
    c.ax.add_patch(mp.Rectangle((414, yb - 104), 10, 104, fc=BRAND_L, ec=BRAND, lw=0.9, zorder=3))
    c.text(419, yb + 18, "평탄화", SMALL, 700, INK)
    c.text(419, yb + 34, "8192", SMALL, 400, MUTED)
    arrow(c, [(402, yb - 20), (414, yb - 20)], head=8)
    for i in range(5):
        circle(c, 458, yb - 92 + i * 20, 6.5, BRAND_L, BRAND, 1.0)
    c.text(458, yb + 18, "완전연결", SMALL, 700, INK)
    c.text(458, yb + 34, "128", SMALL, 400, MUTED)
    for i in range(3):
        y = yb - 74 + i * 26
        circle(c, 508, y, 7, AMBER_L, AMBER, 1.1)
        for j in range(5):
            c.ax.plot([464.5, 501], [yb - 92 + j * 20, y], color="#C9CFD8", lw=0.6, zorder=1)
    for j in range(5):
        c.ax.plot([424, 451.5], [yb - 52, yb - 92 + j * 20], color="#C9CFD8", lw=0.6, zorder=1)
    for i, lb in enumerate(("고양이", "개", "새")):
        c.text(520, yb - 74 + i * 26, lb, SMALL, 600, AMBER_D, ha="left")
    c.text(508, yb + 18, "출력", SMALL, 700, INK)
    c.text(508, yb + 34, "3개 클래스", SMALL, 400, MUTED)
    c.text(200, 14, "특징 추출: 지역 패턴 → 조합된 패턴", SMALL, 600, BRAND_D)
    c.text(480, 14, "분류", SMALL, 600, AMBER_D)
    c.ax.plot([12, 392], [26, 26], color=BRAND, lw=1.0, zorder=2)
    c.ax.plot([414, 548], [26, 26], color=AMBER, lw=1.0, zorder=2)
    return c


# ═════════════════════ RNN ═════════════════════
def fig_rnn():
    c = Canvas("w11_rnn", 560, 222)
    panel_title(c, 12, 14, "(a) 접은 모양")
    b = c.rect(40, 86, 70, 44, BRAND_L, BRAND, lw=1.3, r=6, name="rnnA")
    c.text(75, 108, "RNN", BODY, 700, BRAND_D, owner=b)
    arrow(c, [(75, 170), (75, 130)], BLUE)
    c.text(75, 182, r"$x_t$", BODY, 600, BLUE_D)
    arrow(c, [(75, 86), (75, 50)], AMBER)
    c.text(75, 40, r"$h_t$", BODY, 600, AMBER_D)
    c.ax.add_patch(mp.FancyArrowPatch((110, 100), (110, 118), connectionstyle="arc3,rad=-2.2",
                                      arrowstyle="-|>", mutation_scale=9, color=MUTED, lw=1.2, zorder=4))
    c.text(150, 108, "상태를 다음 시점으로", SMALL, 500, MUTED, ha="left")

    panel_title(c, 250, 14, "(b) 시점별로 펼친 모양")
    xs = [262, 362, 462]
    labs = ("t−1", "t", "t+1")
    for x, lb in zip(xs, labs):
        bb = c.rect(x, 86, 76, 44, BRAND_L, BRAND, lw=1.3, r=6, name="cell" + lb)
        c.text(x + 38, 108, "같은 가중치", SMALL, 600, BRAND_D, owner=bb)
        arrow(c, [(x + 38, 170), (x + 38, 130)], BLUE)
        c.text(x + 38, 182, rf"$x_{{{lb}}}$", BODY, 600, BLUE_D)
        arrow(c, [(x + 38, 86), (x + 38, 50)], AMBER)
        c.text(x + 38, 40, rf"$h_{{{lb}}}$", BODY, 600, AMBER_D)
    for i in range(2):
        arrow(c, [(xs[i] + 76, 108), (xs[i + 1], 108)])
    c.text(400, 206, r"$h_t = \tanh(W_x x_t + W_h h_{t-1} + b)$", BODY, 500, INK)
    return c


# ═════════════════════ LSTM 셀 ═════════════════════
def fig_lstm():
    c = Canvas("w11_lstm", 560, 268)
    cell = c.rect(80, 36, 400, 190, "#F8FAFC", LINE, lw=1.2, r=10, name="cell")
    yC, yH = 62, 196
    # 셀 상태 선
    c.line([(20, yC), (540, yC)], AMBER_D, 2.0, arrow=True, head=11)
    c.text(28, yC - 12, r"$C_{t-1}$", BODY, 600, AMBER_D, ha="left", on_line=False)
    c.text(532, yC - 12, r"$C_t$", BODY, 600, AMBER_D, ha="right")
    c.text(280, 24, "셀 상태: 오래 기억할 정보가 흐르는 길", SMALL, 600, AMBER_D)

    def op(x, y, s):
        circle(c, x, y, 10, WHITE, INK, 1.2, 5)
        c.text(x, y, s, BODY, 700, INK, on_line=True)

    gates = [(140, "σ", "망각"), (220, "σ", "입력"), (290, "tanh", "후보"), (380, "σ", "출력")]
    for x, f, nm in gates:
        b = c.rect(x - 28, 132, 56, 40, BRAND_L, BRAND, lw=1.1, r=4, name="g" + nm, parent=cell)
        c.text(x, 145, f, BODY, 700, BRAND_D, owner=b)
        c.text(x, 162, nm, SMALL, 600, MUTED, owner=b)
    # 아래 입력선
    c.line([(20, yH), (430, yH)], BLUE, 1.4, arrow=False)
    c.text(28, yH + 14, r"$h_{t-1}, x_t$", SMALL, 600, BLUE_D, ha="left")
    for x, _, _ in gates:
        c.ax.plot([x, x], [yH, 172], color=BLUE, lw=1.1, zorder=2)
    # 연산 노드
    op(140, yC, "×")
    op(255, yC, "+")
    op(255, 108, "×")
    op(430, 140, "×")
    c.ax.plot([140, 140], [132, yC + 10], color=BRAND_D, lw=1.1, zorder=2)
    c.ax.plot([220, 220, 245], [132, 108, 108], color=BRAND_D, lw=1.1, zorder=2)
    c.ax.plot([290, 290, 265], [132, 108, 108], color=BRAND_D, lw=1.1, zorder=2)
    c.ax.plot([255, 255], [98, yC + 10], color=BRAND_D, lw=1.1, zorder=2)
    # 출력: tanh(C_t) × o
    tb = c.rect(406, 86, 48, 26, AMBER_L, AMBER, lw=1.0, r=4, name="tanhC", parent=cell)
    c.text(430, 99, "tanh", SMALL, 700, AMBER_D, owner=tb)
    c.ax.plot([430, 430], [yC, 86], color=AMBER_D, lw=1.1, zorder=2)
    c.ax.plot([430, 430], [112, 130], color=AMBER_D, lw=1.1, zorder=2)
    c.ax.plot([408, 420], [140, 140], color=BRAND_D, lw=1.1, zorder=2)
    c.ax.annotate("", xy=(540, 240), xytext=(430, 150), zorder=4,
                  arrowprops=dict(arrowstyle="-|>", color=AMBER_D, lw=1.4, mutation_scale=10,
                                  connectionstyle="angle,angleA=-90,angleB=180", shrinkA=0, shrinkB=0))
    c.text(540, 254, r"$h_t$", BODY, 600, AMBER_D, ha="right")
    return c


# ═════════════════════ Transformer ═════════════════════
def fig_transformer():
    c = Canvas("w11_transformer", 560, 392)
    x, w = 40, 200
    def blk(y, t, sub, fc, ec, tc=INK, h=40):
        return c.box_text((x, y, w, h), t, sub, fc, ec, tcolor=tc)
    blk(330, "입력 토큰", "단어 조각·이미지 패치·시점", BLUE_L, BLUE, BLUE_D)
    blk(270, "임베딩 + 위치 인코딩", "벡터로 바꾸고 순서 정보 더함", BLUE_L, BLUE, BLUE_D)
    grp = c.rect(x - 14, 82, w + 28, 172, WHITE, BRAND, lw=1.3, r=8, ls=(0, (5, 3)), name="블록")
    c.text(x + w + 22, 168, "× N", TITLE, 700, BRAND_D, ha="left")
    ys = [210, 168, 128, 92]
    names = [("멀티헤드 셀프 어텐션", BRAND_L, BRAND), ("더하기·정규화", GRAY_L, LINE),
             ("피드포워드 신경망", BRAND_L, BRAND), ("더하기·정규화", GRAY_L, LINE)]
    for (t, fc, ec), yy in zip(names, ys):
        b = c.rect(x, yy, w, 30, fc, ec, lw=1.1, r=5, name=t + str(yy), parent=grp)
        c.text(x + w / 2, yy + 15, t, BODY, 600, INK, owner=b)
    blk(20, "출력층", "분류·회귀·다음 토큰", AMBER_L, AMBER, AMBER_D)
    cx = x + w / 2
    arrow(c, [(cx, 330), (cx, 310)])
    arrow(c, [(cx, 270), (cx, 240)])
    arrow(c, [(cx, 210), (cx, 198)])
    arrow(c, [(cx, 168), (cx, 158)])
    arrow(c, [(cx, 128), (cx, 122)])
    arrow(c, [(cx, 92), (cx, 60)])
    # 잔차 연결
    c.line([(x - 4, 252), (x - 4, 183), (x, 183)], AMBER_D, 1.2, head=8)
    c.line([(x - 4, 162), (x - 4, 107), (x, 107)], AMBER_D, 1.2, head=8)
    c.text(x - 8, 220, "잔차", SMALL, 600, AMBER_D, ha="right")

    # 오른쪽: 어텐션 가중치
    toks = ["나는", "어제", "책을", "샀다"]
    W_ = np.array([[0.55, 0.15, 0.15, 0.15], [0.1, 0.6, 0.1, 0.2], [0.1, 0.1, 0.5, 0.3], [0.25, 0.15, 0.4, 0.2]])
    gx, gy, s = 360, 112, 40
    c.text(gx + 2 * s, 24, "셀프 어텐션 가중치", BODY, 700, INK)
    c.text(gx + 2 * s, 44, "각 행: 그 단어가 다른 단어를 참고하는 비율", SMALL, 400, MUTED)
    c.text(gx + 2 * s, 66, r"$\mathrm{softmax}(QK^{\top}/\sqrt{d})\,V$", BODY, 500, BRAND_D)
    for i, t in enumerate(toks):
        c.text(gx - 8, gy + i * s + s / 2, t, SMALL, 600, INK, ha="right")
        c.text(gx + i * s + s / 2, gy - 10, t, SMALL, 600, INK)
        for j in range(4):
            v = W_[i, j]
            col = (1 - v * 1.3, 1 - v * 0.55, 1 - v * 0.9)
            col = tuple(max(0, min(1, cc)) for cc in col)
            c.ax.add_patch(mp.Rectangle((gx + j * s, gy + i * s), s, s, fc=col, ec=WHITE, lw=1.2, zorder=3))
            c.text(gx + j * s + s / 2, gy + i * s + s / 2, f"{v:.2f}", SMALL, 600, WHITE if v > 0.45 else INK)
    c.text(gx + 2 * s, gy + 4 * s + 18, "'샀다'는 '책을'을 가장 많이 참고", SMALL, 500, MUTED)
    return c


# ═════════════════════ 전이학습 ═════════════════════
def fig_transfer():
    c = Canvas("w11_transfer", 560, 214)
    panel_title(c, 12, 14, "(a) 사전학습")
    panel_title(c, 304, 14, "(b) 내 과제에 전이")
    for x0, data, head, headsub, note in ((12, "대규모 데이터", "기존 출력층", "1,000개 클래스", "많은 데이터로 일반적 특징 학습"),
                                          (304, "내 데이터", "새 출력층", "3개 클래스", "적은 데이터로 출력층 위주 학습")):
        c.box_text((x0, 36, 244, 34), data, None, BLUE_L, BLUE, tcolor=BLUE_D)
        arrow(c, [(x0 + 122, 70), (x0 + 122, 86)])
        b = c.rect(x0, 86, 244, 54, BRAND_L, BRAND, lw=1.3, r=6, name="bb" + str(x0))
        c.text(x0 + 122, 104, "특징 추출부 (백본)", BODY, 700, BRAND_D, owner=b)
        c.text(x0 + 122, 124, "합성곱 층 또는 트랜스포머 블록", SMALL, 400, MUTED, owner=b)
        arrow(c, [(x0 + 122, 140), (x0 + 122, 156)])
        hb = c.rect(x0 + 42, 156, 160, 34, AMBER_L if x0 > 100 else GRAY_L, AMBER if x0 > 100 else LINE,
                    lw=1.3, r=6, name="hd" + str(x0))
        c.text(x0 + 122, 167, head, SMALL, 700, AMBER_D if x0 > 100 else INK, owner=hb)
        c.text(x0 + 122, 181, headsub, SMALL, 400, MUTED, owner=hb)
        c.text(x0 + 122, 204, note, SMALL, 500, MUTED)
    arrow(c, [(256, 113), (304, 113)], AMBER_D, lw=1.6)
    c.text(280, 90, "가중치", SMALL, 600, AMBER_D)
    c.text(280, 136, "복사", SMALL, 600, AMBER_D)
    return c


FIGS = [fig_process, fig_split, fig_fit, fig_linear, fig_svm, fig_knn, fig_tree, fig_forest, fig_boost,
        fig_unsup, fig_trainloop, fig_mlp, fig_conv, fig_cnn, fig_rnn, fig_lstm, fig_transformer, fig_transfer]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "images")
    os.makedirs(out, exist_ok=True)
    args = sys.argv[1:]
    preview = None
    if "--preview" in args:
        i = args.index("--preview")
        preview = args[i + 1]
        os.makedirs(preview, exist_ok=True)
        del args[i:i + 2]
    ok = True
    for build in FIGS:
        if args and build.__name__.replace("fig_", "") not in args:
            continue
        ok &= build().save(out, preview)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
