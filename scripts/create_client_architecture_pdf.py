from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


OUTPUT = Path(__file__).resolve().parents[1] / "output" / "pdf" / "lakshya-erp-product-architecture.pdf"
WIDTH, HEIGHT = A4

NAVY = HexColor("#102A43")
INK = HexColor("#243B53")
MUTED = HexColor("#627D98")
BLUE = HexColor("#1677C8")
BLUE_DARK = HexColor("#0B5FA5")
PALE_BLUE = HexColor("#EAF4FF")
PALE = HexColor("#F5F9FD")
LINE = HexColor("#D9E2EC")
GREEN = HexColor("#13795B")
AMBER = HexColor("#B45309")


def wrap(c, text, font, size, max_width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if stringWidth(candidate, font, size) <= max_width or not line:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_wrapped(c, text, x, y, width, font="Helvetica", size=11, leading=16, color=INK):
    c.setFillColor(color)
    c.setFont(font, size)
    for line in wrap(c, text, font, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y


def round_rect(c, x, y, w, h, fill, stroke=None, radius=16):
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1 if stroke else 0)


def label(c, text, x, y, color=BLUE):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x, y, text.upper())


def heading(c, title, subtitle=None):
    label(c, "Lakshya ERP / Product architecture", 48, HEIGHT - 48)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(48, HEIGHT - 92, title)
    if subtitle:
        draw_wrapped(c, subtitle, 48, HEIGHT - 118, WIDTH - 96, size=12, leading=18, color=MUTED)


def footer(c, page):
    c.setStrokeColor(LINE)
    c.line(48, 34, WIDTH - 48, 34)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8.5)
    c.drawString(48, 20, "Lakshya Institution | Product concept by SrS Logics")
    c.drawRightString(WIDTH - 48, 20, f"{page} / 4")


def title_page(c):
    c.setFillColor(NAVY)
    c.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.circle(WIDTH - 84, HEIGHT - 118, 130, fill=1, stroke=0)
    c.setFillColor(BLUE_DARK)
    c.circle(WIDTH - 16, HEIGHT - 284, 175, fill=1, stroke=0)

    label(c, "Lakshya Institution", 52, HEIGHT - 66, PALE_BLUE)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 38)
    c.drawString(52, HEIGHT - 132, "A connected ERP")
    c.drawString(52, HEIGHT - 178, "for everyday institute work.")
    draw_wrapped(
        c,
        "A single operating system for admissions, student records, academic delivery, fees, parent communication, and leadership visibility.",
        52,
        HEIGHT - 222,
        390,
        size=14,
        leading=21,
        color=PALE_BLUE,
    )

    y = 140
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 19)
    c.drawString(52, y + 74, "Designed around real institute operations.")
    items = [
        ("Admissions first", "Track every enquiry, counsellor action, follow-up, and conversion."),
        ("One student record", "Connect fees, attendance, exams, communication, and parent access."),
        ("Built to grow", "Start with one centre and expand through secure, reusable modules."),
    ]
    card_w = (WIDTH - 120) / 3
    for index, (name, body) in enumerate(items):
        x = 52 + index * (card_w + 8)
        round_rect(c, x, y - 8, card_w, 62, white, LINE, 12)
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(x + 12, y + 33, name)
        draw_wrapped(c, body, x + 12, y + 17, card_w - 24, size=8.7, leading=11, color=MUTED)

    footer(c, 1)
    c.showPage()


def system_page(c):
    heading(c, "One system, connected end to end.", "Each module serves a clear team, while sharing the same student, batch, and activity record.")

    y = 550
    modules = [
        ("Admissions CRM", "Enquiries, counselling, follow-ups, conversion", BLUE),
        ("Student Core", "Profiles, parents, documents, enrolments", NAVY),
        ("Academic Operations", "Batches, timetable, faculty, attendance, exams", GREEN),
        ("Fees & Communication", "Plans, dues, receipts, notices, parent updates", AMBER),
    ]
    for index, (name, body, colour) in enumerate(modules):
        x = 48 + (index % 2) * 255
        row_y = y - (index // 2) * 112
        round_rect(c, x, row_y, 231, 88, white, LINE, 14)
        c.setFillColor(colour)
        c.circle(x + 22, row_y + 61, 8, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(x + 40, row_y + 56, name)
        draw_wrapped(c, body, x + 18, row_y + 34, 194, size=9.3, leading=13, color=MUTED)

    label(c, "Shared system foundation", 48, 291)
    round_rect(c, 48, 154, WIDTH - 96, 116, PALE_BLUE, None, 16)

    nodes = [
        ("Staff and parents", 78, 88),
        ("Lakshya ERP", 185, 96),
        ("Secure API", 301, 82),
        ("Institute database", 403, 114),
    ]
    for index, (name, x, width) in enumerate(nodes):
        round_rect(c, x, 198, width, 38, white, LINE, 10)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 8.8)
        c.drawCentredString(x + width / 2, 213, name)
        if index < len(nodes) - 1:
            c.setStrokeColor(BLUE)
            c.setLineWidth(1.4)
            c.line(x + width, 217, nodes[index + 1][1] - 10, 217)
            c.setFillColor(BLUE)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(nodes[index + 1][1] - 15, 213, ">")

    draw_wrapped(
        c,
        "The web app and API are delivered together as one managed service. The database stays separate and protected, so the product remains simple for the institute and maintainable as modules grow.",
        70,
        181,
        WIDTH - 140,
        size=10.5,
        leading=15,
        color=INK,
    )
    footer(c, 2)
    c.showPage()


def role_page(c):
    heading(c, "The right view for every person.", "The ERP does not show the same dashboard to everyone. Each role sees the actions and information needed for their day.")
    roles = [
        ("Owner / Director", "Admissions health, collections, approvals, branch performance, and exception alerts.", "Decisions"),
        ("Admissions Team", "Lead desk, tasks, calls, counselling, follow-ups, and conversion handoff.", "Conversion"),
        ("Academic & Accounts", "Batches, attendance, fees, receipts, timetable, exam activity, and student records.", "Operations"),
        ("Parents & Students", "Attendance, fee status, timetable, results, notices, and support requests.", "Visibility"),
    ]
    for index, (name, body, tag) in enumerate(roles):
        x = 48 + (index % 2) * 255
        y = 513 - (index // 2) * 156
        round_rect(c, x, y, 231, 128, white, LINE, 15)
        round_rect(c, x + 16, y + 91, 76, 21, PALE_BLUE, None, 10)
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x + 54, y + 98, tag.upper())
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 15)
        c.drawString(x + 16, y + 67, name)
        draw_wrapped(c, body, x + 16, y + 46, 196, size=9.5, leading=14, color=MUTED)

    label(c, "Product experience", 48, 172)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 21)
    c.drawString(48, 141, "Focused workspaces, not crowded pages.")
    draw_wrapped(
        c,
        "Every page has one primary job: create a lead, handle a follow-up, record attendance, collect a payment, or review a student. Details open only when they are needed.",
        48,
        116,
        WIDTH - 96,
        size=11,
        leading=16,
        color=INK,
    )
    footer(c, 3)
    c.showPage()


def launch_page(c):
    heading(c, "Admissions first. Built to expand.", "The first release establishes a usable workflow and the shared data foundation for every future module.")
    steps = [
        ("01", "Lead capture", "Website, walk-in, calls, WhatsApp, referrals, and campaigns enter one pipeline."),
        ("02", "Counsellor control", "Assignment, task ownership, notes, counselling, reminders, and an accountable follow-up rhythm."),
        ("03", "Admission conversion", "Confirmed leads become a student record without duplicate data entry."),
        ("04", "Connected expansion", "Fees, batches, attendance, parent updates, reporting, and academic operations follow on the same foundation."),
    ]
    for index, (number, name, body) in enumerate(steps):
        x = 48
        y = 548 - index * 102
        c.setStrokeColor(LINE)
        c.setLineWidth(1)
        c.line(98, y - 19, WIDTH - 48, y - 19)
        c.setFillColor(BLUE)
        c.circle(70, y + 7, 21, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(70, y + 3, number)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(110, y + 8, name)
        draw_wrapped(c, body, 110, y - 14, WIDTH - 160, size=10.3, leading=15, color=MUTED)

    round_rect(c, 48, 88, WIDTH - 96, 70, NAVY, None, 14)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(68, 128, "The result")
    draw_wrapped(
        c,
        "Lakshya gains one reliable source of truth for every lead, student, payment, class, parent interaction, and decision.",
        68,
        107,
        WIDTH - 136,
        size=10.5,
        leading=15,
        color=PALE_BLUE,
    )
    footer(c, 4)
    c.showPage()


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT), pagesize=A4)
    pdf.setTitle("Lakshya ERP Product Architecture")
    pdf.setAuthor("SrS Logics")
    title_page(pdf)
    system_page(pdf)
    role_page(pdf)
    launch_page(pdf)
    pdf.save()
    print(OUTPUT)


if __name__ == "__main__":
    main()
