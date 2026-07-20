from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "lakshya-erp-product-architecture.pdf"
PAGE_W, PAGE_H = A4

INK = HexColor("#102A43")
INK_2 = HexColor("#334E68")
SLATE = HexColor("#627D98")
LINE = HexColor("#D9E2EC")
CANVAS = HexColor("#F4F8FC")
SURFACE = HexColor("#FFFFFF")
SURFACE_MUTED = HexColor("#EEF4FA")
BLUE = HexColor("#1677C8")
BLUE_DARK = HexColor("#0B5FA5")
TEAL = HexColor("#13795B")
ORANGE = HexColor("#B45309")


def para(c, text, x, y_top, width, style):
    flow = Paragraph(text, style)
    _, height = flow.wrap(width, PAGE_H)
    flow.drawOn(c, x, y_top - height)
    return height


def style(size=10, leading=None, color=INK_2, font="Helvetica", bold=False, align=TA_LEFT):
    return ParagraphStyle(
        name=f"s{size}{font}{bold}{align}",
        fontName="Helvetica-Bold" if bold else font,
        fontSize=size,
        leading=leading or size * 1.35,
        textColor=color,
        alignment=align,
        spaceAfter=0,
    )


BODY = style(10.2, 14.5)
BODY_SMALL = style(8.7, 11.6)
BODY_WHITE = style(10.2, 14.5, white)
KICKER = style(8.5, 11, BLUE, bold=True)
KICKER_WHITE = style(8.5, 11, HexColor("#B9DDFF"), bold=True)
H1 = style(31, 36, INK, bold=True)
H1_WHITE = style(31, 36, white, bold=True)
H2 = style(21, 26, INK, bold=True)
H3 = style(12, 15, INK, bold=True)
H3_WHITE = style(12, 15, white, bold=True)
NUMBER = style(17, 19, BLUE, bold=True)


def rounded(c, x, y, w, h, fill, stroke=None, radius=12, line_width=0.8):
    c.setLineWidth(line_width)
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.roundRect(x, y, w, h, radius, stroke=1 if stroke else 0, fill=1)


def line(c, x1, y1, x2, y2, color=LINE, width=0.8):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)


def arrow(c, x1, y1, x2, y2, color=SLATE, width=1.1):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)
    direction = 1 if x2 >= x1 else -1
    c.line(x2, y2, x2 - 5 * direction, y2 + 3)
    c.line(x2, y2, x2 - 5 * direction, y2 - 3)


def footer(c, page, label="Lakshya ERP | Product Architecture"):
    line(c, 20 * mm, 15 * mm, PAGE_W - 20 * mm, 15 * mm)
    c.setFont("Helvetica", 7.8)
    c.setFillColor(SLATE)
    c.drawString(20 * mm, 9.8 * mm, label)
    c.drawRightString(PAGE_W - 20 * mm, 9.8 * mm, f"Page {page}")


def pill(c, text, x, y, fill=HexColor("#DCEEFF"), text_color=BLUE_DARK):
    c.setFont("Helvetica-Bold", 8)
    width = stringWidth(text, "Helvetica-Bold", 8) + 16
    rounded(c, x, y, width, 21, fill, radius=10.5)
    c.setFillColor(text_color)
    c.drawCentredString(x + width / 2, y + 7, text)
    return width


def page_cover(c):
    c.setFillColor(CANVAS)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(INK)
    c.rect(0, PAGE_H - 74 * mm, PAGE_W, 74 * mm, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.circle(PAGE_W - 24 * mm, PAGE_H - 18 * mm, 48 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor("#48A9E6"))
    c.circle(PAGE_W - 64 * mm, PAGE_H - 47 * mm, 19 * mm, fill=1, stroke=0)

    para(c, "LAKSHYA ERP", 24 * mm, PAGE_H - 29 * mm, 100 * mm, KICKER_WHITE)
    para(c, "Product Architecture<br/>and Design Direction", 24 * mm, PAGE_H - 45 * mm, 145 * mm, H1_WHITE)
    para(c, "A practical blueprint for one connected institute operating system.", 24 * mm, PAGE_H - 83 * mm, 135 * mm, BODY)

    y = PAGE_H - 119 * mm
    para(c, "The outcome", 24 * mm, y, 75 * mm, KICKER)
    para(c, "One system that turns every enquiry into a managed student journey - admissions, fees, academics, attendance, communication, and leadership reporting all working from the same data.", 24 * mm, y - 10 * mm, 105 * mm, style(15, 21, INK, bold=True))

    cards = [
        ("01", "Admissions first", "Capture enquiries, own follow-ups, and convert confirmed leads without leakage."),
        ("02", "One student record", "Connect parent, batch, fee, attendance, result, and communication history."),
        ("03", "Built for operations", "Focused role workspaces instead of one crowded dashboard."),
    ]
    y = 48 * mm
    card_w = 51 * mm
    for index, (num, title, copy) in enumerate(cards):
        x = 24 * mm + index * (card_w + 7 * mm)
        rounded(c, x, y, card_w, 44 * mm, SURFACE, LINE, 10)
        para(c, num, x + 7 * mm, y + 37 * mm, 20 * mm, NUMBER)
        para(c, title, x + 7 * mm, y + 27 * mm, card_w - 14 * mm, H3)
        para(c, copy, x + 7 * mm, y + 15 * mm, card_w - 14 * mm, style(7.2, 9.4, INK_2))

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(SLATE)
    c.drawString(24 * mm, 27 * mm, "Prepared by SrS Logics")
    c.drawRightString(PAGE_W - 24 * mm, 27 * mm, "Product foundation | July 2026")


def page_architecture(c):
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    para(c, "SYSTEM ARCHITECTURE", 20 * mm, PAGE_H - 23 * mm, 100 * mm, KICKER)
    para(c, "One deployment. One source of truth.", 20 * mm, PAGE_H - 33 * mm, 170 * mm, H2)
    para(c, "The first release stays simple: a single secure web application, a managed PostgreSQL database, and integrations added only when operations require them.", 20 * mm, PAGE_H - 47 * mm, 166 * mm, BODY)

    x = 20 * mm
    y = PAGE_H - 118 * mm
    w = PAGE_W - 40 * mm
    rounded(c, x, y, w, 58 * mm, CANVAS, LINE, 12)

    node_y = y + 21 * mm
    nodes = [
        (x + 8 * mm, "Staff and parents", "Browser or installed web app", HexColor("#E9F4FF")),
        (x + 55 * mm, "Lakshya ERP", "Single Render web service", HexColor("#DCEEFF")),
        (x + 102 * mm, "FastAPI", "Business rules and permissions", HexColor("#DDF5EE")),
        (x + 149 * mm, "PostgreSQL", "Supabase managed database", HexColor("#FFF3DE")),
    ]
    node_w = 37 * mm
    for i, (nx, title, copy, fill) in enumerate(nodes):
        rounded(c, nx, node_y, node_w, 21 * mm, fill, LINE, 8)
        para(c, title, nx + 4 * mm, node_y + 15 * mm, node_w - 8 * mm, style(9.2, 11, INK, bold=True, align=TA_CENTER))
        para(c, copy, nx + 4 * mm, node_y + 8.5 * mm, node_w - 8 * mm, style(6.9, 8.6, INK_2, align=TA_CENTER))
        if i < len(nodes) - 1:
            arrow(c, nx + node_w, node_y + 10.5 * mm, nodes[i + 1][0] - 3 * mm, node_y + 10.5 * mm)

    para(c, "How modules connect", 20 * mm, y - 12 * mm, 120 * mm, H3)
    para(c, "Every module shares the same people, academic structure, and activity history. A confirmed admission becomes a student record without duplicate data entry.", 20 * mm, y - 20 * mm, 166 * mm, BODY)

    modules = [
        ("Admissions CRM", "Enquiries, follow-ups, counselling, conversion", BLUE),
        ("Student & Parent", "Profiles, documents, enrollment, access", TEAL),
        ("Academics", "Courses, batches, timetable, faculty, exams", HexColor("#5A78A8")),
        ("Finance", "Fee plans, invoices, payments, receipts", ORANGE),
        ("Communication", "WhatsApp, SMS, notices, delivery history", HexColor("#7A5CA8")),
        ("Reporting", "Role-aware decisions and audit-ready data", INK_2),
    ]
    start_y = y - 58 * mm
    for i, (title, copy, color) in enumerate(modules):
        col, row = i % 3, i // 3
        bx = 20 * mm + col * 59 * mm
        by = start_y - row * 31 * mm
        rounded(c, bx, by, 54 * mm, 24 * mm, SURFACE, LINE, 9)
        c.setFillColor(color)
        c.circle(bx + 8 * mm, by + 16 * mm, 3 * mm, fill=1, stroke=0)
        para(c, title, bx + 14 * mm, by + 19 * mm, 34 * mm, style(9.5, 11, INK, bold=True))
        para(c, copy, bx + 7 * mm, by + 10 * mm, 40 * mm, BODY_SMALL)

    footer(c, 2)


def page_experience(c):
    c.setFillColor(CANVAS)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    para(c, "PRODUCT EXPERIENCE", 20 * mm, PAGE_H - 23 * mm, 100 * mm, KICKER)
    para(c, "Focused screens for real work.", 20 * mm, PAGE_H - 33 * mm, 170 * mm, H2)
    para(c, "The interface is intentionally not one giant dashboard. Each role sees a focused workspace with a clear next action and just enough context to complete it.", 20 * mm, PAGE_H - 47 * mm, 165 * mm, BODY)

    x = 20 * mm
    y = PAGE_H - 177 * mm
    screen_w = 80 * mm
    screen_h = 102 * mm
    rounded(c, x, y, screen_w, screen_h, INK, None, 12)
    rounded(c, x + 8 * mm, y + 8 * mm, screen_w - 16 * mm, screen_h - 16 * mm, SURFACE, None, 8)
    c.setFillColor(SURFACE_MUTED)
    c.roundRect(x + 8 * mm, y + screen_h - 24 * mm, screen_w - 16 * mm, 16 * mm, 8, fill=1, stroke=0)
    para(c, "Admissions CRM", x + 14 * mm, y + screen_h - 13.5 * mm, 42 * mm, style(8.6, 10, INK, bold=True))
    pill(c, "Create lead", x + 56 * mm, y + screen_h - 18.5 * mm)
    para(c, "Today", x + 14 * mm, y + screen_h - 32 * mm, 38 * mm, style(7.5, 9, SLATE, bold=True))
    for i, label in enumerate(["12 new leads", "8 follow-ups due", "4 parent visits", "2 fee approvals"]):
        row_y = y + screen_h - 44 * mm - i * 11 * mm
        rounded(c, x + 14 * mm, row_y, 51 * mm, 8 * mm, SURFACE_MUTED, None, 4)
        para(c, label, x + 17 * mm, row_y + 5.8 * mm, 40 * mm, style(6.9, 8, INK_2))
    para(c, "Selected lead", x + 14 * mm, y + 23 * mm, 38 * mm, style(7.4, 9, SLATE, bold=True))
    rounded(c, x + 14 * mm, y + 12 * mm, 51 * mm, 9 * mm, HexColor("#DDF5EE"), None, 4)
    para(c, "Aarav Thakre - call at 6:30 PM", x + 17 * mm, y + 18 * mm, 45 * mm, style(6.5, 7.6, TEAL, bold=True))

    rx = 114 * mm
    para(c, "Admissions begins with three workspaces", rx, PAGE_H - 78 * mm, 75 * mm, H3)
    items = [
        ("Overview", "A manager can assess the entire pipeline in under 30 seconds: new leads, follow-ups due, hot leads, conversions, source quality, and counsellor load."),
        ("Lead Desk", "Counsellors work from a searchable lead table with a selected profile, follow-up timeline, notes, and quick actions. No broad institute dashboard here."),
        ("New Lead", "A guided intake flow captures every enquiry and creates the first owner and follow-up before the record is saved."),
    ]
    top = PAGE_H - 94 * mm
    for i, (title, copy) in enumerate(items):
        cy = top - i * 39 * mm
        rounded(c, rx, cy - 25 * mm, 76 * mm, 31 * mm, SURFACE, LINE, 9)
        c.setFillColor(BLUE)
        c.circle(rx + 9 * mm, cy - 4 * mm, 4 * mm, fill=1, stroke=0)
        para(c, str(i + 1).zfill(2), rx + 6.2 * mm, cy - 1.4 * mm, 6 * mm, style(6.5, 7.5, white, bold=True, align=TA_CENTER))
        para(c, title, rx + 18 * mm, cy + 1 * mm, 50 * mm, H3)
        para(c, copy, rx + 8 * mm, cy - 8 * mm, 60 * mm, BODY_SMALL)

    para(c, "Shared interaction rules", 20 * mm, 67 * mm, 100 * mm, H3)
    rules = [
        ("One job per screen", "Avoids crowded, dashboard-like modules."),
        ("Clear primary action", "Create, save, mark, send, or record is always visible."),
        ("Responsive by default", "Sidebar becomes a mobile drawer; data tables become compact records."),
        ("Accessible and accountable", "Labels, keyboard focus, status text, and audit history are built in."),
    ]
    for i, (title, copy) in enumerate(rules):
        bx = 20 * mm + (i % 2) * 86 * mm
        by = 22 * mm + (1 - i // 2) * 18 * mm
        c.setFillColor(BLUE if i < 2 else TEAL)
        c.circle(bx + 3 * mm, by + 7.5 * mm, 2 * mm, fill=1, stroke=0)
        para(c, title, bx + 8 * mm, by + 12 * mm, 60 * mm, style(8.5, 10, INK, bold=True))
        para(c, copy, bx + 8 * mm, by + 5.5 * mm, 67 * mm, style(7.2, 8.7, INK_2))

    footer(c, 3)


def page_roadmap(c):
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    para(c, "DELIVERY ROADMAP", 20 * mm, PAGE_H - 23 * mm, 100 * mm, KICKER)
    para(c, "A controlled path to go-live.", 20 * mm, PAGE_H - 33 * mm, 170 * mm, H2)
    para(c, "The system grows in connected stages. Each stage delivers a usable operating outcome before the next begins.", 20 * mm, PAGE_H - 47 * mm, 166 * mm, BODY)

    stages = [
        ("01", "Admissions foundation", "Live leads, follow-ups, ownership, notes, lead stages, conversion, and user access.", BLUE),
        ("02", "Student and fee handoff", "Student profile, documents, course and batch allocation, fee plans, invoices, receipts, and dues.", TEAL),
        ("03", "Academic operations", "Timetable, faculty allocation, attendance, exams, results, and intervention notes.", HexColor("#5A78A8")),
        ("04", "Parent experience and control", "Parent access, notices, payment links, progress visibility, reporting, audit history, and automation.", ORANGE),
    ]
    top = PAGE_H - 77 * mm
    for i, (num, title, copy, color) in enumerate(stages):
        by = top - i * 38 * mm
        rounded(c, 20 * mm, by - 27 * mm, PAGE_W - 40 * mm, 31 * mm, SURFACE, LINE, 10)
        c.setFillColor(color)
        c.circle(34 * mm, by - 11.5 * mm, 8.5 * mm, fill=1, stroke=0)
        para(c, num, 29.3 * mm, by - 7.8 * mm, 9.4 * mm, style(7.4, 8.8, white, bold=True, align=TA_CENTER))
        para(c, title, 47 * mm, by - 4 * mm, 70 * mm, H3)
        para(c, copy, 47 * mm, by - 12 * mm, 128 * mm, BODY_SMALL)

    y = 52 * mm
    rounded(c, 20 * mm, y, PAGE_W - 40 * mm, 30 * mm, INK, None, 10)
    para(c, "What this architecture protects", 28 * mm, y + 22 * mm, 90 * mm, H3_WHITE)
    points = ["No duplicate student data", "No lost admission follow-ups", "No hidden role permissions", "No integration lock-in"]
    for i, point in enumerate(points):
        px = 28 * mm + (i % 2) * 80 * mm
        py = y + 11 * mm - (i // 2) * 8 * mm
        c.setFillColor(HexColor("#6DD5B5"))
        c.circle(px, py + 1 * mm, 1.6 * mm, fill=1, stroke=0)
        para(c, point, px + 5 * mm, py + 3.5 * mm, 63 * mm, style(8.1, 9.4, white, bold=True))

    para(c, "Next immediate step", 20 * mm, 42 * mm, 100 * mm, KICKER)
    para(c, "Build the Admissions CRM as the first complete, usable module - with staff login, real lead data, follow-ups, and the admission-to-student handoff.", 20 * mm, 33 * mm, 165 * mm, style(12, 16, INK, bold=True))
    footer(c, 4)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    c.setTitle("Lakshya ERP - Product Architecture and Design")
    c.setAuthor("SrS Logics")
    c.setSubject("Lakshya ERP software architecture and product design direction")
    for page in (page_cover, page_architecture, page_experience, page_roadmap):
        page(c)
        c.showPage()
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
