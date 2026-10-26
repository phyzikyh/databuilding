# -*- coding: utf-8 -*-
"""10주차 이론 그림(벡터 SVG) 생성 스크립트.

실행: python make_figures_w10.py [--preview <폴더>]
  → images/w10_*.svg 생성. 캔버스 도구와 레이아웃 검사는 make_figures_w9.py의 Canvas를 그대로 쓴다.
"""
import os
import sys
import matplotlib.patches as mp
from matplotlib.patches import FancyBboxPatch

from make_figures_w9 import (Canvas, INK, MUTED, LINE, BRAND, BRAND_D, BLUE, BLUE_D, BLUE_L,
                             AMBER, AMBER_D, AMBER_L, WHITE, GRAY_L, TITLE, BODY, SMALL)

OBJ_LINE = "#9DB7DB"
OBJ_FILL = "#C9D8EE"
OVERLAP = "#BDE8DA"


def chip(c, parent, x, y, label, fc=AMBER):
    """클래스 이름표."""
    w = 8 + 10 * len(label)
    b = c.rect(x, y, w, 15, fc, fc, lw=1.0, r=3, name=f"칩 {label}@{x:.0f}", parent=parent, z=5)
    c.text(x + w / 2, y + 7.5, label, SMALL, 700, WHITE, owner=b)
    return w


def draw_scene(c, frame, ox, oy, mode):
    """170×100 프레임 안의 거리 장면. mode: 'cls' | 'det' | 'seg'."""
    ground = oy + 88
    person = dict(box=(ox + 22, oy + 39, 18, 49), head=(ox + 31, oy + 46, 5), body=(ox + 24, oy + 52, 14, 36))
    car = dict(box=(ox + 70, oy + 48, 82, 40), body=(ox + 72, oy + 62, 78, 20), cabin=(ox + 88, oy + 50, 46, 16),
               wheels=((ox + 88, oy + 82), (ox + 134, oy + 82)))

    def paint(fill, edge, lw, car_fill=None):
        cf = car_fill or fill
        c.ax.add_patch(mp.Circle(person["head"][:2], person["head"][2], fc=fill, ec=edge, lw=lw, zorder=2))
        bx, by, bw, bh = person["body"]
        c.ax.add_patch(FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0,rounding_size=4",
                                      fc=fill, ec=edge, lw=lw, zorder=2))
        for key, r_ in (("body", 6), ("cabin", 5)):
            x, y, w, h = car[key]
            c.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r_}",
                                          fc=cf, ec=edge, lw=lw, zorder=2))
        for wx, wy in car["wheels"]:
            c.ax.add_patch(mp.Circle((wx, wy), 6, fc=edge if car_fill is None else cf, ec=edge, lw=lw, zorder=3))

    if mode == "seg":
        c.ax.add_patch(mp.Rectangle((ox, ground), 170, 12, fc="#DDE6F2", ec="none", zorder=1.5))
        paint("#F0A860", AMBER_D, 0.8, car_fill="#F7CC9E")
        return
    c.ax.plot([ox, ox + 170], [ground, ground], color=OBJ_LINE, lw=1.0, zorder=1.5)
    paint(OBJ_FILL, OBJ_LINE, 0.9)
    if mode == "cls":
        chip(c, frame, ox + 6, oy + 6, "거리")
    if mode == "det":
        for d, label in ((person, "보행자"), (car, "자동차")):
            x, y, w, h = d["box"]
            c.rect(x, y, w, h, "none", AMBER, lw=1.8, r=0, name=f"상자 {label}", parent=frame, z=4)
            chip(c, frame, x, y - 15, label)


# ═════════════════════════════ 그림 10-1: 분류·검출·분할 ═════════════════════════════
def fig_levels():
    c = Canvas("w10_levels", 560, 190)
    titles = ("(a) 이미지 분류", "(b) 객체 검출", "(c) 분할")
    notes = ("사진 한 장에 범주 하나", "대상마다 사각형과 범주", "픽셀마다 범주")
    modes = ("cls", "det", "seg")
    for i in range(3):
        px = 15 + 180 * i
        c.text(px, 14, titles[i], TITLE, 600, INK, ha="left")
        frame = c.rect(px, 30, 170, 100, BLUE_L, BLUE, lw=1.2, r=4, name=f"프레임{i}")
        draw_scene(c, frame, px, 30, modes[i])
        c.text(px + 85, 146, notes[i], BODY, 500, INK)
    c.text(280, 164, "표시하는 정보와 작업량이 늘어납니다", SMALL, 500, MUTED)
    c.line([(15, 178), (545, 178)], LINE, 1.4)
    return c


# ═════════════════════════════ 그림 10-2: 좌표계와 박스 계산 ═════════════════════════════
def fig_bbox():
    c = Canvas("w10_bbox", 560, 248)
    c.text(14, 12, "(a) 이미지 좌표계", TITLE, 600, INK, ha="left")
    c.text(274, 12, "(b) 저장된 두 점에서 박스 계산", TITLE, 600, INK, ha="left")

    fx, fy, fw, fh = 38, 44, 200, 160          # 이미지 1픽셀 = 1pt
    frame = c.rect(fx, fy, fw, fh, BLUE_L, BLUE, lw=1.2, r=3, name="이미지")
    # 축: 원점은 왼쪽 위
    c.line([(fx, fy - 12), (fx + 62, fy - 12)], MUTED, 1.3)
    c.text(fx + 72, fy - 12, "x", BODY, 600, MUTED)
    c.line([(fx - 12, fy), (fx - 12, fy + 62)], MUTED, 1.3)
    c.text(fx - 12, fy + 73, "y", BODY, 600, MUTED)
    c.ax.add_patch(mp.Circle((fx, fy), 3.2, fc=INK, ec=WHITE, lw=0.8, zorder=6))
    c.text(fx + 8, fy + 10, "(0, 0)", SMALL, 500, BLUE_D, ha="left", owner=frame)

    # 박스: x=40, y=30, w=120, h=110
    bx, by, bw, bh = fx + 40, fy + 30, 120, 110
    c.rect(bx, by, bw, bh, WHITE, AMBER, lw=1.9, r=0, name="박스", parent=frame, z=3)
    for (px, py) in ((bx, by), (bx + bw, by + bh)):
        c.ax.add_patch(mp.Circle((px, py), 3.2, fc=AMBER_D, ec=WHITE, lw=0.8, zorder=6))
    c.text(bx + 8, by + 11, "(x, y)", SMALL, 600, AMBER_D, ha="left", owner=frame)
    c.text(bx + bw - 8, by + bh - 11, "(x+w, y+h)", SMALL, 600, AMBER_D, ha="right", owner=frame)
    # 너비·높이 표시
    mx = bx + bw / 2
    c.line([(mx, by + 36), (bx + 8, by + 36)], AMBER_D, 1.2, head=8)
    c.line([(mx, by + 36), (bx + bw - 8, by + 36)], AMBER_D, 1.2, head=8)
    c.text(bx + bw / 2, by + 26, "w", BODY, 600, AMBER_D)
    my = by + bh / 2 + 4
    c.line([(bx + 24, my), (bx + 24, by + 46)], AMBER_D, 1.2, head=8)
    c.line([(bx + 24, my), (bx + 24, by + bh - 24)], AMBER_D, 1.2, head=8)
    c.text(bx + 38, my, "h", BODY, 600, AMBER_D)
    c.text(fx + fw / 2, fy + fh + 17, "원점은 왼쪽 위이고, y는 아래로 커집니다", SMALL, 400, MUTED)

    # (b) 저장된 점 → 박스
    rx, rw = 274, 272
    js = c.rect(rx, 32, rw, 50, GRAY_L, LINE, lw=1.0, r=5, name="JSON")
    c.text(rx + 12, 47, '"points": [[160, 140], [40, 30]]', BODY, 500, INK, ha="left", owner=js)
    c.text(rx + 12, 68, "클릭한 순서대로 저장되어 첫 점이 오른쪽 아래일 수 있음", SMALL, 400, MUTED, ha="left", owner=js)
    c.line([(rx + rw / 2, 82), (rx + rw / 2, 100)], MUTED)
    calc = c.rect(rx, 100, rw, 84, WHITE, BRAND, lw=1.3, r=5, name="계산")
    lines = ("x = min(160, 40) = 40", "y = min(140, 30) = 30", "w = |160 − 40| = 120", "h = |140 − 30| = 110")
    for k, s in enumerate(lines):
        c.text(rx + 14, 114 + 18 * k, s, BODY, 400, INK, ha="left", owner=calc)
    c.line([(rx + rw / 2, 184), (rx + rw / 2, 202)], MUTED)
    res = c.rect(rx, 202, rw, 32, AMBER_L, AMBER, lw=1.5, r=5, name="결과")
    c.text(rx + rw / 2, 218, "(x, y, w, h) = (40, 30, 120, 110)", BODY, 700, AMBER_D, owner=res)
    return c


# ═════════════════════════════ 그림 10-3: 겹침 정도와 IoU ═════════════════════════════
def fig_iou():
    c = Canvas("w10_iou", 560, 232)
    A = (100, 80)
    shifts = ((5, 5), (20, 13), (50, 27))
    for i, (dx, dy) in enumerate(shifts):
        px = 14 + 180 * i
        frame = c.rect(px, 14, 172, 150, WHITE, LINE, lw=1.0, r=5, name=f"패널{i}", z=0.5)
        ax_, ay_ = px + 12, 46
        bx_, by_ = ax_ + dx, ay_ + dy
        inter = (A[0] - dx) * (A[1] - dy)
        iou = inter / (2 * A[0] * A[1] - inter)
        c.rect(bx_, by_, A[0] - dx, A[1] - dy, OVERLAP, BRAND, lw=0.8, r=0, name=f"겹침{i}", parent=frame, z=1)
        c.rect(ax_, ay_, A[0], A[1], "none", AMBER, lw=1.8, r=0, name=f"참값{i}", parent=frame, z=3)
        c.rect(bx_, by_, A[0], A[1], "none", BLUE, lw=1.8, r=0, name=f"작업자{i}", parent=frame, z=3, ls=(0, (5, 3)))
        c.text(px + 86, 30, f"IoU = {iou:.2f}", TITLE, 700, INK)
    # 범례
    ly = 184
    c.rect(150, ly - 5, 18, 10, "none", AMBER, lw=1.8, r=0, name="범례1")
    c.text(174, ly, "참값 상자", SMALL, 500, INK, ha="left")
    c.rect(256, ly - 5, 18, 10, "none", BLUE, lw=1.8, r=0, name="범례2", ls=(0, (3, 2)))
    c.text(280, ly, "작업자 상자", SMALL, 500, INK, ha="left")
    c.rect(374, ly - 5, 18, 10, OVERLAP, BRAND, lw=0.8, r=0, name="범례3")
    c.text(398, ly, "겹친 부분", SMALL, 500, INK, ha="left")
    c.text(280, 210, "IoU = 겹친 면적 ÷ 합친 면적", BODY, 600, BRAND_D)
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
    for build in (fig_levels, fig_bbox, fig_iou):
        ok &= build().save(out, preview)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
