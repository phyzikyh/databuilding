from pathlib import Path
import html
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Preformatted,
    Spacer, Table, TableStyle, PageBreak
)

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "week02-lab.qmd"
OUTPUT = ROOT / "2주차_코딩실습_변경본.pdf"

font_regular = Path(r"C:\Windows\Fonts\malgun.ttf")
font_bold = Path(r"C:\Windows\Fonts\malgunbd.ttf")
pdfmetrics.registerFont(TTFont("Malgun", str(font_regular)))
pdfmetrics.registerFont(TTFont("Malgun-Bold", str(font_bold)))

styles = getSampleStyleSheet()
body = ParagraphStyle("BodyKR", parent=styles["BodyText"], fontName="Malgun",
                      fontSize=9.4, leading=15, spaceAfter=5)
h1 = ParagraphStyle("H1KR", parent=body, fontName="Malgun-Bold", fontSize=20,
                    leading=28, textColor=colors.HexColor("#17324D"), spaceAfter=12)
h2 = ParagraphStyle("H2KR", parent=body, fontName="Malgun-Bold", fontSize=15,
                    leading=21, textColor=colors.HexColor("#17324D"),
                    spaceBefore=13, spaceAfter=8)
h3 = ParagraphStyle("H3KR", parent=body, fontName="Malgun-Bold", fontSize=11.5,
                    leading=17, textColor=colors.HexColor("#1AB18B"),
                    spaceBefore=9, spaceAfter=5)
code_style = ParagraphStyle("CodeKR", fontName="Malgun", fontSize=7.1,
                            leading=10, leftIndent=5, rightIndent=5,
                            borderColor=colors.HexColor("#D8DEE5"), borderWidth=.5,
                            borderPadding=6, backColor=colors.HexColor("#F6F8FA"),
                            spaceBefore=4, spaceAfter=7)
note = ParagraphStyle("NoteKR", parent=body, leftIndent=8, rightIndent=6,
                      borderColor=colors.HexColor("#1AB18B"), borderWidth=.8,
                      borderPadding=7, backColor=colors.HexColor("#F0FBF7"))


def inline(text):
    text = html.escape(text.strip())
    text = re.sub(r"`([^`]+)`", r'<font name="Malgun-Bold">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r'<b>\1</b>', text)
    text = re.sub(r"\*([^*]+)\*", r'<i>\1</i>', text)
    return text


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Malgun", 8)
    canvas.setFillColor(colors.HexColor("#667085"))
    canvas.drawString(18 * mm, 11 * mm, "데이터구축실습 · 2주차 코딩실습 변경본")
    canvas.drawRightString(192 * mm, 11 * mm, str(doc.page))
    canvas.restoreState()


doc = BaseDocTemplate(str(OUTPUT), pagesize=A4,
                      rightMargin=17 * mm, leftMargin=17 * mm,
                      topMargin=16 * mm, bottomMargin=18 * mm,
                      title="2주차 코딩실습 변경본")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
doc.addPageTemplates(PageTemplate(id="content", frames=[frame], onPage=footer))

lines = SOURCE.read_text(encoding="utf-8").splitlines()
story = []
in_code = False
code = []
table_rows = []
in_answer = False


def flush_table():
    global table_rows
    if not table_rows:
        return
    data = []
    for row in table_rows:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            continue
        data.append([Paragraph(inline(c), body) for c in cells])
    if data:
        widths = [doc.width / len(data[0])] * len(data[0])
        tbl = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
        tbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Malgun"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF7F3")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#17324D")),
            ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#CCD5DE")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.extend([tbl, Spacer(1, 6)])
    table_rows = []


for raw in lines:
    line = raw.rstrip()
    if line.startswith("```"):
        flush_table()
        if in_code:
            story.append(Preformatted("\n".join(code), code_style, maxLineLength=105))
            code = []
            in_code = False
        else:
            in_code = True
        continue
    if in_code:
        code.append(line)
        continue
    if line.startswith("|") and line.endswith("|"):
        table_rows.append(line)
        continue
    flush_table()
    if line.startswith("::: {.callout"):
        in_answer = True
        continue
    if line == ":::":
        in_answer = False
        story.append(Spacer(1, 4))
        continue
    if not line or line.startswith("<!--"):
        story.append(Spacer(1, 3))
    elif line.startswith("# "):
        story.append(Paragraph(inline(line[2:]), h1))
    elif line.startswith("## "):
        story.append(Paragraph(inline(line[3:]), h2))
    elif line.startswith("### "):
        story.append(Paragraph(inline(line[4:]), h3))
    elif re.match(r"^[-*] ", line):
        story.append(Paragraph("• " + inline(line[2:]), note if in_answer else body))
    elif re.match(r"^\d+\. ", line):
        story.append(Paragraph(inline(line), note if in_answer else body))
    else:
        story.append(Paragraph(inline(line), note if in_answer else body))

flush_table()
doc.build(story)
print(OUTPUT)
