# -*- coding: utf-8 -*-
"""9주차 이론 그림(벡터 SVG) 생성 스크립트.

실행: python make_figures_w9.py [--preview <폴더>]
  → images/w9_*.svg 생성. 글자는 외곽선(path)으로 변환되어 글꼴이 없는 환경에서도 모양이 같다.

설계 원칙
  - 캔버스 1단위 = 1pt. 책 본문 폭(약 750px)에 맞추면 10pt 글자는 약 14px로 보인다.
  - 색은 의미가 있을 때만 쓴다: 청록=처리·흐름, 파랑=입력 데이터, 앰버=정답·되돌림·강조.
  - 모든 그림은 생성 직후 레이아웃 검사를 통과해야 저장된다
    (글자가 박스 안에 들어가는지, 글자끼리·글자와 선이 겹치지 않는지, 박스끼리 겹치지 않는지).
"""
import os
import sys
import itertools
import matplotlib
import matplotlib.patches
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

plt.rcParams.update({
    "font.family": "Noto Sans KR",
    "svg.fonttype": "path",
    "svg.hashsalt": "w9",
    "mathtext.fontset": "stix",
    "axes.unicode_minus": False,
})

# ── 팔레트: 본문 스타일의 브랜드 청록을 중심으로 한 색맹 안전 조합 ──
INK, MUTED, LINE = "#1F2937", "#5B6472", "#98A1AE"
BRAND, BRAND_D, BRAND_L = "#1AB18B", "#0F6F57", "#E6F6F1"
BLUE, BLUE_D, BLUE_L = "#3C6EB4", "#2B5287", "#EAF1FA"
AMBER, AMBER_D, AMBER_L = "#E4842B", "#9A4D07", "#FDF1E3"
WHITE, GRAY_L = "#FFFFFF", "#F3F4F6"

TITLE, BODY, SMALL, CHIP = 11.5, 10.5, 9.5, 9.0     # 글자 크기(pt)


class Canvas:
    """pt 단위 좌표계(위쪽이 y=0)와 레이아웃 검사를 가진 그림 캔버스."""

    def __init__(self, name, W, H):
        self.name, self.W, self.H = name, W, H
        self.fig = plt.figure(figsize=(W / 72, H / 72), dpi=72)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, W)
        self.ax.set_ylim(H, 0)          # 위가 0
        self.ax.axis("off")
        self.boxes, self.texts, self.segs = [], [], []

    # ── 도형 ──
    def rect(self, x, y, w, h, fc=WHITE, ec=LINE, lw=1.0, r=5, ls="-", name=None, parent=None, z=2):
        if r:
            p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                               fc=fc, ec=ec, lw=lw, ls=ls, zorder=z)
        else:
            p = Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, ls=ls, zorder=z)
        self.ax.add_patch(p)
        self.boxes.append(dict(name=name or f"box{len(self.boxes)}", x=x, y=y, w=w, h=h, parent=parent))
        return self.boxes[-1]

    def text(self, x, y, s, size=BODY, weight=400, color=INK, ha="center", va="center",
             owner=None, style="normal", on_line=False):
        t = self.ax.text(x, y, s, fontsize=size, fontweight=weight, color=color, ha=ha, va=va,
                         fontstyle=style, zorder=6)
        self.texts.append(dict(t=t, owner=owner, on_line=on_line, s=s))
        return t

    def box_text(self, bx, title, sub=None, fc=WHITE, ec=LINE, tcolor=INK, scolor=MUTED, lw=1.0, r=5, ls="-"):
        """제목(굵게) + 보조 설명 한 줄로 이루어진 박스."""
        b = self.rect(bx[0], bx[1], bx[2], bx[3], fc=fc, ec=ec, lw=lw, r=r, ls=ls, name=title)
        cx, cy = bx[0] + bx[2] / 2, bx[1] + bx[3] / 2
        if sub:
            self.text(cx, cy - 8.5, title, TITLE, 600, tcolor, owner=b)
            self.text(cx, cy + 9.5, sub, SMALL, 400, scolor, owner=b)
        else:
            self.text(cx, cy, title, TITLE, 600, tcolor, owner=b)
        return b

    # ── 선·화살표 ──
    def line(self, pts, color=LINE, lw=1.3, ls="-", arrow=True, head=11):
        """꺾은선. 마지막 구간 끝에 화살촉을 단다(점선일 때도 화살촉은 실선)."""
        segs = list(zip(pts[:-1], pts[1:]))
        dashed = ls != "-"
        for k, ((x0, y0), (x1, y1)) in enumerate(segs):
            last = k == len(segs) - 1
            self.segs.append((x0, y0, x1, y1))
            if last and arrow:
                if dashed:      # 점선 본체 + 실선 화살촉 구간(10pt)
                    L = max(abs(x1 - x0), abs(y1 - y0))
                    ux, uy = (x1 - x0) / L, (y1 - y0) / L
                    hx, hy = x1 - ux * 10, y1 - uy * 10
                    self.ax.plot([x0, hx], [y0, hy], color=color, lw=lw, ls=ls, zorder=3, solid_capstyle="butt")
                    x0, y0 = hx, hy
                self.ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=4,
                                 arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls="-",
                                                 shrinkA=0, shrinkB=0, mutation_scale=head,
                                                 joinstyle="miter", capstyle="butt"))
            else:
                self.ax.plot([x0, x1], [y0, y1], color=color, lw=lw, ls=ls, zorder=3,
                             solid_capstyle="butt", solid_joinstyle="miter")

    # ── 검사 ──
    def _bbox(self, t):
        r = self.fig.canvas.get_renderer()
        bb = t.get_window_extent(r)
        # 디스플레이(아래가 0) → 데이터(위가 0)
        x0, x1 = bb.x0, bb.x1
        y0, y1 = self.H - bb.y1, self.H - bb.y0
        return x0, y0, x1, y1

    @staticmethod
    def _inter(a, b, pad=0.0):
        return not (a[2] + pad <= b[0] or b[2] + pad <= a[0] or a[3] + pad <= b[1] or b[3] + pad <= a[1])

    @staticmethod
    def _seg_hits(seg, box, pad=1.5):
        x0, y0, x1, y1 = seg
        bx0, by0, bx1, by1 = box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad
        # 축에 평행한 선분만 사용하므로 구간 겹침으로 판정
        if abs(x1 - x0) < 1e-6:     # 세로선
            return bx0 < x0 < bx1 and not (max(y0, y1) <= by0 or min(y0, y1) >= by1)
        if abs(y1 - y0) < 1e-6:     # 가로선
            return by0 < y0 < by1 and not (max(x0, x1) <= bx0 or min(x0, x1) >= bx1)
        return False

    def check(self):
        self.fig.canvas.draw()
        bad, M = [], 6.0
        tb = [(d, self._bbox(d["t"])) for d in self.texts]
        for d, bb in tb:
            label = d["s"].replace("\n", " ")[:24]
            o = d["owner"]
            if o is not None:     # 글자는 소속 박스 안쪽 여백 3pt 이상
                if bb[0] < o["x"] + 3 or bb[2] > o["x"] + o["w"] - 3 or bb[1] < o["y"] + 1.5 or bb[3] > o["y"] + o["h"] - 1.5:
                    bad.append(f"박스 이탈: '{label}' (글자 {bb[2]-bb[0]:.0f}pt, 박스 {o['w']:.0f}pt)")
            if bb[0] < M or bb[1] < M - 2 or bb[2] > self.W - M or bb[3] > self.H - M + 2:
                bad.append(f"캔버스 여백 부족: '{label}'")
        for (d1, b1), (d2, b2) in itertools.combinations(tb, 2):
            if self._inter(b1, b2, pad=1.0):
                bad.append(f"글자 겹침: '{d1['s'][:14]}' × '{d2['s'][:14]}'")
        for d, bb in tb:
            if d["on_line"]:
                continue
            for seg in self.segs:
                if self._seg_hits(seg, bb):
                    bad.append(f"선·글자 겹침: '{d['s'][:16]}'")
                    break
        top = [b for b in self.boxes if b["parent"] is None]
        for a, b in itertools.combinations(top, 2):
            if self._inter((a["x"], a["y"], a["x"] + a["w"], a["y"] + a["h"]),
                           (b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"]), pad=2.0):
                bad.append(f"박스 겹침: {a['name']} × {b['name']}")
        min_font = min(d["t"].get_fontsize() for d in self.texts)
        return bad, min_font

    def save(self, outdir, preview=None):
        bad, min_font = self.check()
        status = "통과" if not bad else f"실패 {len(bad)}건"
        print(f"[{self.name}] {self.W}x{self.H}pt, 글자 {len(self.texts)}개, 최소 {min_font:.1f}pt → 레이아웃 검사 {status}")
        for b in bad:
            print("   -", b)
        if bad:
            plt.close(self.fig)
            return False
        self.fig.savefig(os.path.join(outdir, f"{self.name}.svg"), format="svg", facecolor="white")
        if preview:
            self.fig.savefig(os.path.join(preview, f"{self.name}.png"), dpi=200, facecolor="white")
        plt.close(self.fig)
        return True


# ═════════════════════════════ 그림 9-1: 지도학습의 구조 ═════════════════════════════
def fig_supervised():
    c = Canvas("w9_supervised", 560, 186)
    ya, h, gap = 14, 56, 44
    yb = ya + h + gap
    c.text(12, ya + h / 2, "(a) 학습", TITLE, 600, INK, ha="left")
    c.text(12, yb + h / 2, "(b) 예측", TITLE, 600, INK, ha="left")

    # (a) 학습: 입력 쌍 (X, y) → 모델 학습 → 학습된 모델
    grp = c.rect(86, ya, 186, h, WHITE, LINE, lw=1.0, r=6, name="학습 데이터 쌍")
    bx = c.rect(92, ya + 6, 84, h - 12, BLUE_L, BLUE, name="X셀", parent=grp)
    c.text(92 + 42, ya + h / 2 - 7, r"특성 $X$", TITLE, 600, BLUE_D, owner=bx)
    c.text(92 + 42, ya + h / 2 + 9, "입력 데이터", SMALL, 400, MUTED, owner=bx)
    by = c.rect(182, ya + 6, 84, h - 12, AMBER_L, AMBER, lw=1.6, name="y셀", parent=grp)
    c.text(182 + 42, ya + h / 2 - 7, r"정답 $y$", TITLE, 600, AMBER_D, owner=by)
    c.text(182 + 42, ya + h / 2 + 9, "라벨", SMALL, 600, AMBER_D, owner=by)
    c.box_text((306, ya, 106, h), "모델 학습", r"$X$와 $y$의 규칙", BRAND_L, BRAND)
    c.box_text((446, ya, 104, h), "학습된 모델", r"규칙 $f$", WHITE, INK, lw=1.4)
    c.line([(272, ya + h / 2), (306, ya + h / 2)], MUTED)
    c.line([(412, ya + h / 2), (446, ya + h / 2)], MUTED)

    # (b) 예측: 새 X → 학습된 모델 → 예측값
    c.box_text((86, yb, 186, h), r"새 특성 $X$", "정답 없이 입력만 있음", BLUE_L, BLUE, tcolor=BLUE_D)
    c.box_text((306, yb, 106, h), "학습된 모델", r"규칙 $f$", WHITE, INK, lw=1.4)
    c.box_text((446, yb, 104, h), r"예측값 $\hat{y}$", "새 데이터의 답", AMBER_L, AMBER, tcolor=AMBER_D)
    c.line([(272, yb + h / 2), (306, yb + h / 2)], MUTED)
    c.line([(412, yb + h / 2), (446, yb + h / 2)], MUTED)

    # 학습 결과를 예측에 재사용
    ymid = ya + h + gap / 2
    c.line([(498, ya + h), (498, ymid), (359, ymid), (359, yb)], BRAND, 1.5)
    c.text(430, ymid - 11, "학습한 규칙을 예측에 사용", SMALL, 500, BRAND_D)
    return c


# ═════════════════════════════ 그림 9-2: 데이터의 단계 ═════════════════════════════
def fig_stages():
    c = Canvas("w9_stages", 560, 200)
    y, h, w = 22, 58, 132
    xs = [14, 214, 414]
    c.box_text((xs[0], y, w, h), "원시데이터", "수집한 그대로", GRAY_L, LINE)
    c.box_text((xs[1], y, w, h), "원천데이터", "정제를 마친 데이터", BLUE_L, BLUE, tcolor=BLUE_D)
    c.box_text((xs[2], y, w, h), "가공데이터", "참값·속성·주석", AMBER_L, AMBER, tcolor=AMBER_D)
    for i, name in enumerate(("정제", "라벨링")):
        x0, x1 = xs[i] + w, xs[i + 1]
        c.line([(x0 + 1, y + h / 2), (x1 - 1, y + h / 2)], MUTED)
        c.text((x0 + x1) / 2, y + h / 2 - 12, name, BODY, 600, BRAND_D)

    # 학습 데이터셋: 원천 + 가공의 쌍
    yd = 136
    ds = c.box_text((xs[1], yd, xs[2] + w - xs[1], 46), "학습 데이터셋", "원천데이터와 가공데이터를 짝지은 것", BRAND_L, BRAND, lw=1.5)
    c.line([(xs[1] + w / 2, y + h), (xs[1] + w / 2, yd)], MUTED)
    c.line([(xs[2] + w / 2, y + h), (xs[2] + w / 2, yd)], MUTED)
    # 색 범례: 그림 9-1과 같은 의미(파랑=입력 X, 앰버=정답 y)
    for k, (fc, ec, txt) in enumerate(((BLUE_L, BLUE, r"모델의 입력 $X$"), (AMBER_L, AMBER, r"정답 $y$"))):
        yy = yd + 6 + k * 22
        c.rect(14, yy, 14, 14, fc, ec, lw=1.2, r=3, name=f"범례{k}")
        c.text(36, yy + 7, txt, SMALL, 400, INK, ha="left")
    return c


# ═════════════════════════════ 그림 9-3: 라벨링 작업 흐름 ═════════════════════════════
def fig_flow():
    c = Canvas("w9_flow", 560, 404)
    x, w, h = 170, 220, 48
    ys = [14, 94, 174, 254, 334]
    spec = [
        ("준비", "원천 데이터 확인 · 가이드라인 · 교육", BRAND_L, BRAND, INK),
        ("파일럿 작업", "소량으로 시험", BRAND_L, BRAND, INK),
        ("본 작업", "전량 라벨링", BRAND_L, BRAND, INK),
        ("검수", "교차검사 · 전문가 검수", BRAND_L, BRAND, INK),
        ("가공데이터 확정", "원천데이터와 짝지어 학습 데이터셋 구성", BLUE_L, BLUE, BLUE_D),
    ]
    for (t, s, fc, ec, tc), yy in zip(spec, ys):
        c.box_text((x, yy, w, h), t, s, fc, ec, tcolor=tc)
    # 아래로 흐르는 주 경로
    cx = x + w / 2
    for i in range(4):
        c.line([(cx, ys[i] + h), (cx, ys[i + 1])], MUTED)
    c.text(cx + 10, ys[1] + h + 16, "통과", SMALL, 600, MUTED, ha="left")
    c.text(cx + 10, ys[3] + h + 16, "통과", SMALL, 600, MUTED, ha="left")

    # 되돌림 1: 파일럿 → 준비 (오른쪽)
    xr = x + w + 36
    c.line([(x + w, ys[1] + h / 2), (xr, ys[1] + h / 2), (xr, ys[0] + h / 2), (x + w + 1, ys[0] + h / 2)], AMBER, 1.5, ls=(0, (5, 3)))
    c.text(xr + 12, ys[0] + h + 14, "기준이 모호함", SMALL, 600, AMBER_D, ha="left")
    c.text(xr + 12, ys[0] + h + 30, "→ 기준 수정", SMALL, 400, AMBER_D, ha="left")

    # 되돌림 2: 검수 → 본 작업 (왼쪽)
    xl = x - 36
    c.line([(x, ys[3] + h / 2), (xl, ys[3] + h / 2), (xl, ys[2] + h / 2), (x - 1, ys[2] + h / 2)], AMBER, 1.5, ls=(0, (5, 3)))
    c.text(xl - 12, ys[2] + h + 14, "반려 기준 초과", SMALL, 600, AMBER_D, ha="right")
    c.text(xl - 12, ys[2] + h + 30, "→ 원인 분석·보완", SMALL, 400, AMBER_D, ha="right")
    return c


# ═════════════════════════════ 그림 9-4: 라벨 저장 구조(ER) ═════════════════════════════
def entity(c, x, y, w, name, rows, key_col=True):
    """엔티티 표: 머리행 + 속성행(자료형, 이름, 키 표시)."""
    hh, rh = 26, 22
    H = hh + rh * len(rows)
    outer = c.rect(x, y, w, H, WHITE, BRAND, lw=1.3, r=4, name=name)
    c.rect(x, y, w, hh, BRAND_L, BRAND, lw=1.3, r=4, name=name + "_head", parent=outer)
    c.text(x + w / 2, y + hh / 2, name, TITLE, 600, BRAND_D, owner=outer)
    for i, (typ, nm, key) in enumerate(rows):
        yy = y + hh + rh * i
        if i:
            c.ax.plot([x, x + w], [yy, yy], color="#E5E7EB", lw=0.8, zorder=2)
        c.text(x + 10, yy + rh / 2, typ, SMALL, 400, MUTED, ha="left", owner=outer)
        c.text(x + 56, yy + rh / 2, nm, BODY, 500 if key in ("PK", "FK") else 400, INK, ha="left", owner=outer)
        if key:
            col, fc, ec = {"PK": (AMBER_D, AMBER_L, AMBER), "FK": (BLUE_D, BLUE_L, BLUE),
                           "UQ": (MUTED, GRAY_L, LINE)}[key]
            cw = 28
            chip = c.rect(x + w - cw - 8, yy + 4, cw, rh - 8, fc, ec, lw=0.9, r=3, name=f"{name}.{nm}.{key}", parent=outer)
            c.text(x + w - cw / 2 - 8, yy + rh / 2, key, CHIP, 700, col, owner=chip)
    return outer, H


def one_end(c, x, y, direction=+1, color=MUTED):
    """'정확히 하나' 표기: 선에 수직인 짧은 이중 막대."""
    for dy in (6, 11):
        yy = y + direction * dy
        c.ax.plot([x - 6, x + 6], [yy, yy], color=color, lw=1.4, zorder=4, solid_capstyle="butt")


def many_end(c, x, y_line_end, y_box, color=MUTED):
    """'여러 개' 표기: 까마귀발. 선 끝(y_line_end)에서 박스 윗변(y_box)으로 세 갈래."""
    for dx in (-7, 0, 7):
        c.ax.plot([x, x + dx], [y_line_end, y_box], color=color, lw=1.4, zorder=4, solid_capstyle="butt")


def fig_schema():
    c = Canvas("w9_schema", 560, 360)
    top, gap = 14, 64
    ls, h1 = entity(c, 14, top, 200, "label_schema",
                    [("int", "label_id", "PK"), ("text", "label_name", "UQ"), ("text", "description", "")])
    sm, h2 = entity(c, 346, top, 200, "samples",
                    [("int", "sample_id", "PK"), ("text", "content", ""), ("text", "data_type", "")])
    ya = top + max(h1, h2) + gap
    an, h3 = entity(c, 100, ya, 360, "annotations",
                    [("int", "anno_id", "PK"), ("int", "sample_id", "FK"), ("int", "label_id", "FK"),
                     ("text", "annotator", ""), ("text", "guideline_version", ""), ("text", "created_at", "")])
    # 관계선: 각 엔티티 아래 중앙 → annotations 윗변
    for cx, label, side in ((114, "정의된 라벨만 사용", "R"), (446, "샘플마다 여러 라벨", "L")):
        y0, y1 = top + h1, ya
        c.line([(cx, y0 + 12), (cx, y1 - 12)], MUTED, 1.4, arrow=False)
        one_end(c, cx, y0, +1)
        many_end(c, cx, y1 - 12, y1)
        if side == "R":
            c.text(cx + 12, (y0 + y1) / 2, label, SMALL, 500, MUTED, ha="left")
        else:
            c.text(cx - 12, (y0 + y1) / 2, label, SMALL, 500, MUTED, ha="right")
    c.text(280, ya + h3 + 18, "UNIQUE (sample_id, annotator): 같은 작업자는 한 샘플에 한 번만 라벨을 붙임",
           SMALL, 400, MUTED)
    c.H = ya + h3 + 34
    c.fig.set_size_inches(c.W / 72, c.H / 72)
    c.ax.set_ylim(c.H, 0)
    return c


# ═════════════════════════════ 그림 9-5: 객체 검출 라벨의 예 ═════════════════════════════
def fig_detect():
    c = Canvas("w9_detect", 560, 236)
    c.text(14, 14, "(a) 이미지 위의 바운딩 박스", TITLE, 600, INK, ha="left")
    c.text(340, 14, "(b) 라벨 기록", TITLE, 600, INK, ha="left")

    # (a) 1280×720 이미지를 300pt 폭으로 줄여 그린다(배율 300/1280)
    fx, fy, fw = 14, 30, 300
    fh = fw * 720 / 1280
    k = fw / 1280
    frame = c.rect(fx, fy, fw, fh, BLUE_L, BLUE, lw=1.2, r=4, name="이미지")
    c.text(fx + 6, fy + 9, "(0, 0)", SMALL, 400, BLUE_D, ha="left", owner=frame)
    ground = fy + 600 * k
    c.ax.plot([fx, fx + fw], [ground, ground], color="#9DB7DB", lw=1.0, zorder=2)

    def pt(px, py):
        return fx + px * k, fy + py * k

    OBJ = "#C9D8EE"
    # 보행자 (머리 + 몸통)
    x0, y0 = pt(140, 280); x1, y1 = pt(250, 600)
    mid = (x0 + x1) / 2
    c.ax.add_patch(matplotlib.patches.Circle((mid, y0 + 9), 6.5, fc=OBJ, ec="#9DB7DB", lw=0.9, zorder=2))
    c.ax.add_patch(FancyBboxPatch((x0 + 3, y0 + 19), (x1 - x0) - 6, (y1 - y0) - 21,
                                  boxstyle="round,pad=0,rounding_size=5", fc=OBJ, ec="#9DB7DB", lw=0.9, zorder=2))
    # 자동차 (차체 + 바퀴)
    cx0, cy0 = pt(520, 340); cx1, cy1 = pt(980, 580)
    c.ax.add_patch(FancyBboxPatch((cx0 + 3, cy0 + 12), (cx1 - cx0) - 6, (cy1 - cy0) - 24,
                                  boxstyle="round,pad=0,rounding_size=7", fc=OBJ, ec="#9DB7DB", lw=0.9, zorder=2))
    c.ax.add_patch(FancyBboxPatch((cx0 + 26, cy0 + 2), (cx1 - cx0) - 52, 16,
                                  boxstyle="round,pad=0,rounding_size=6", fc=OBJ, ec="#9DB7DB", lw=0.9, zorder=2))
    for wx in (cx0 + 22, cx1 - 22):
        c.ax.add_patch(matplotlib.patches.Circle((wx, cy1 - 12), 7, fc="#9DB7DB", ec="#9DB7DB", lw=0.9, zorder=3))

    # 라벨(앰버): 상자 + 클래스 칩 + 꼭짓점 좌표
    for (a, b, cls) in (((x0, y0), (x1, y1), "보행자"), ((cx0, cy0), (cx1, cy1), "자동차")):
        c.rect(a[0], a[1], b[0] - a[0], b[1] - a[1], "none", AMBER, lw=1.8, r=0, name=f"상자 {cls}", parent=frame, z=4)
        cw = 12 + 11 * len(cls)
        chip = c.rect(a[0], a[1] - 15, cw, 15, AMBER, AMBER, lw=1.0, r=3, name=f"칩 {cls}", parent=frame, z=5)
        c.text(a[0] + cw / 2, a[1] - 7.5, cls, SMALL, 700, WHITE, owner=chip)
    for (px, py) in ((cx0, cy0), (cx1, cy1)):
        c.ax.add_patch(matplotlib.patches.Circle((px, py), 2.8, fc=AMBER_D, ec=WHITE, lw=0.8, zorder=6))
    c.text(cx0 - 6, cy0 + 8, "(520, 340)", SMALL, 500, AMBER_D, ha="right")
    c.text(cx1, cy1 + 11, "(980, 580)", SMALL, 500, AMBER_D, ha="right")
    c.text(fx + fw / 2, fy + fh + 16, "원점은 왼쪽 위이고, x는 오른쪽으로 y는 아래로 커짐", SMALL, 400, MUTED)

    # (b) 라벨 기록 표
    tx, tw = 340, 206
    c.text(tx, 36, "street_0017.jpg  (1280×720)", SMALL, 500, MUTED, ha="left")
    cols = [("클래스", 46), ("x_min", 40), ("y_min", 40), ("x_max", 40), ("y_max", 40)]
    rows = [("자동차", "520", "340", "980", "580"), ("보행자", "140", "280", "250", "600")]
    ty, hh, rh = 50, 24, 26
    outer = c.rect(tx, ty, tw, hh + rh * len(rows), WHITE, AMBER, lw=1.3, r=4, name="기록표")
    head = c.rect(tx, ty, tw, hh, AMBER_L, AMBER, lw=1.3, r=4, name="기록표 머리", parent=outer)
    xx = tx
    for j, (name, w) in enumerate(cols):
        c.text(xx + w / 2, ty + hh / 2, name, SMALL, 700, AMBER_D, owner=outer)
        for i, row in enumerate(rows):
            yy = ty + hh + rh * i
            if j == 0 and i:
                c.ax.plot([tx, tx + tw], [yy, yy], color="#E5E7EB", lw=0.8, zorder=2)
            c.text(xx + w / 2, yy + rh / 2, row[j], BODY, 600 if j == 0 else 400, INK, owner=outer)
        xx += w
    note_y = ty + hh + rh * len(rows) + 22
    c.text(tx, note_y, "객체 하나에 행 하나", SMALL, 600, INK, ha="left")
    c.text(tx, note_y + 17, "(x_min, y_min): 상자의 왼쪽 위", SMALL, 400, MUTED, ha="left")
    c.text(tx, note_y + 33, "(x_max, y_max): 상자의 오른쪽 아래", SMALL, 400, MUTED, ha="left")
    return c


# ═════════════════════════════ 그림 9-6: 상자의 일치도(IoU) ═════════════════════════════
def fig_iou():
    c = Canvas("w9_iou", 560, 192)
    frame = c.rect(14, 14, 250, 164, WHITE, LINE, lw=1.0, r=5, name="도해")
    gt = (50, 46, 100, 80)       # 참값 상자
    wk = (70, 56, 100, 80)       # 작업자 상자: (+20, +10)만큼 어긋남
    c.rect(wk[0], wk[1], gt[0] + gt[2] - wk[0], gt[1] + gt[3] - wk[1], "#BDE8DA", BRAND, lw=0.8, r=0,
           name="겹침", parent=frame, z=1)
    c.rect(*gt, "none", AMBER, lw=1.8, r=0, name="참값 상자", parent=frame, z=3)
    c.rect(*wk, "none", BLUE, lw=1.8, r=0, name="작업자 상자", parent=frame, z=3, ls=(0, (5, 3)))
    c.text(gt[0], gt[1] - 11, "참값 상자", SMALL, 700, AMBER_D, ha="left")
    c.text(wk[0] + wk[2], wk[1] + wk[3] + 12, "작업자 상자", SMALL, 700, BLUE_D, ha="right")
    c.text(110, 93, "겹침", SMALL, 600, BRAND_D)

    x = 300
    c.text(x, 30, "IoU", TITLE, 700, INK, ha="left")
    c.text(x + 30, 30, "=", TITLE, 400, INK, ha="left")
    c.line([(x + 54, 30), (x + 150, 30)], INK, 1.2, arrow=False)
    c.text(x + 102, 17, "겹친 면적", BODY, 500, BRAND_D)
    c.text(x + 102, 44, "합친 면적", BODY, 500, INK)
    c.text(x, 76, "두 상자(가로 100, 세로 80)가 (20, 10)만큼 어긋난 경우", SMALL, 600, INK, ha="left")
    c.text(x, 98, "겹친 면적  80 × 70 = 5,600", BODY, 400, INK, ha="left")
    c.text(x, 118, "합친 면적  8,000 + 8,000 − 5,600 = 10,400", BODY, 400, INK, ha="left")
    c.text(x, 144, "IoU = 5,600 ÷ 10,400 ≈ 0.54", BODY, 600, AMBER_D, ha="left")
    c.text(x, 164, "일치하면 1, 전혀 겹치지 않으면 0", SMALL, 400, MUTED, ha="left")
    return c


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "images")
    os.makedirs(out, exist_ok=True)
    preview = None
    if "--preview" in sys.argv:
        preview = sys.argv[sys.argv.index("--preview") + 1]
        os.makedirs(preview, exist_ok=True)
    ok = True
    for build in (fig_supervised, fig_stages, fig_flow, fig_schema, fig_detect, fig_iou):
        ok &= build().save(out, preview)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
