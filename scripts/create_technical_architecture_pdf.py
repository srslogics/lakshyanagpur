from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


OUTPUT = Path(__file__).resolve().parents[1] / "output" / "pdf" / "lakshya-erp-technical-architecture.pdf"
WIDTH, HEIGHT = landscape(A4)

NAVY = HexColor("#102A43")
INK = HexColor("#243B53")
MUTED = HexColor("#627D98")
BLUE = HexColor("#1476C9")
BLUE_DARK = HexColor("#0B5FA5")
SKY = HexColor("#EAF4FF")
PALE = HexColor("#F7FAFD")
LINE = HexColor("#D9E2EC")
GREEN = HexColor("#13795B")
GREEN_PALE = HexColor("#E6F5EE")
AMBER = HexColor("#B45309")
AMBER_PALE = HexColor("#FEF3E3")


def wrap(c, text, font, size, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if not current or stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def text_block(c, text, x, y, width, font="Helvetica", size=9, leading=12, color=INK, center=False):
    c.setFillColor(color)
    c.setFont(font, size)
    for line in wrap(c, text, font, size, width):
        if center:
            c.drawCentredString(x + width / 2, y, line)
        else:
            c.drawString(x, y, line)
        y -= leading
    return y


def rounded(c, x, y, w, h, fill, stroke=None, radius=10):
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1 if stroke else 0)


def label(c, value, x, y, color=BLUE):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x, y, value.upper())


def page_title(c, title, subtitle, page):
    c.setFillColor(NAVY)
    c.rect(0, HEIGHT - 70, WIDTH, 70, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 19)
    c.drawString(34, HEIGHT - 39, title)
    c.setFillColor(HexColor("#B9D8F5"))
    c.setFont("Helvetica", 8.8)
    c.drawRightString(WIDTH - 34, HEIGHT - 36, subtitle)
    c.setStrokeColor(LINE)
    c.line(34, 26, WIDTH - 34, 26)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.8)
    c.drawString(34, 13, "Lakshya ERP | Technical architecture | SrS Logics")
    c.drawRightString(WIDTH - 34, 13, f"{page} / 3")


def arrow(c, x1, y1, x2, y2, color=BLUE, dashed=False):
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.35)
    if dashed:
        c.setDash(4, 3)
    c.line(x1, y1, x2, y2)
    c.line(x2, y2, x2 - 6, y2 + 3)
    c.line(x2, y2, x2 - 6, y2 - 3)
    c.restoreState()


def box(c, x, y, w, h, title, body, tone=BLUE, implementation=None):
    rounded(c, x, y, w, h, white, LINE, 10)
    c.setFillColor(tone)
    c.rect(x, y + h - 6, w, 6, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10.3)
    c.drawString(x + 12, y + h - 23, title)
    text_block(c, body, x + 12, y + h - 39, w - 24, size=7.8, leading=10.2, color=MUTED)
    if implementation:
        fill = GREEN_PALE if implementation == "implemented" else AMBER_PALE
        ink = GREEN if implementation == "implemented" else AMBER
        tag = "IMPLEMENTED" if implementation == "implemented" else "NEXT"
        rounded(c, x + 12, y + 10, 58 if implementation == "implemented" else 31, 14, fill, None, 7)
        c.setFillColor(ink)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawCentredString(x + 41 if implementation == "implemented" else x + 27.5, y + 14.2, tag)


def architecture_page(c):
    page_title(c, "Lakshya ERP - Target software architecture", "Modular monolith | Single deployed application", 1)
    label(c, "Architecture pattern", 34, 498)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(34, 475, "One application. Clear module boundaries. Shared institute data.")
    text_block(c, "The product runs as one FastAPI application with separate domain modules. This avoids the cost and complexity of microservices while keeping each future module independently maintainable.", 34, 456, 560, size=8.7, leading=12, color=MUTED)

    # Connectors first: browser -> delivery -> API -> database / integrations.
    arrow(c, 184, 358, 218, 358)
    arrow(c, 366, 358, 402, 358)
    arrow(c, 562, 358, 602, 358)
    arrow(c, 482, 273, 482, 230)
    arrow(c, 562, 333, 672, 333, AMBER, dashed=True)

    label(c, "Client layer", 34, 421)
    box(c, 34, 304, 150, 104, "Responsive web and PWA", "Owner dashboard, admissions CRM, staff workspaces, parent and student access. Mobile navigation becomes a drawer.", BLUE, "implemented")

    label(c, "Delivery", 218, 421)
    box(c, 218, 304, 148, 104, "Render web service", "HTTPS endpoint serving the product UI and the API together. One deployment and one public address.", BLUE_DARK, "implemented")

    label(c, "Application layer", 402, 421)
    box(c, 402, 304, 160, 104, "FastAPI modular monolith", "REST routes, request validation, role checks, domain services, and SQLAlchemy data access.", GREEN, "implemented")

    label(c, "Data layer", 602, 421)
    box(c, 602, 304, 205, 104, "Supabase PostgreSQL", "Institute records, admissions activity, students, fee ledger, attendance, results, and audit history.", GREEN, "implemented")

    # Domain services in the app boundary.
    rounded(c, 218, 177, 344, 88, SKY, BLUE, 12)
    label(c, "Domain modules inside the FastAPI application", 234, 244)
    domain_boxes = [
        (234, "Admissions", "implemented"),
        (312, "Students", "next"),
        (390, "Finance", "next"),
        (468, "Academic", "next"),
    ]
    for x, name, state in domain_boxes:
        fill = GREEN_PALE if state == "implemented" else white
        stroke = GREEN if state == "implemented" else LINE
        rounded(c, x, 194, 66, 31, fill, stroke, 8)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawCentredString(x + 33, 207, name)

    # Integration boundary.
    rounded(c, 672, 155, 135, 110, PALE, AMBER, 12)
    label(c, "Integration boundary", 685, 244, AMBER)
    integrations = ["WhatsApp / SMS", "Payment gateway", "Email / files"]
    for index, value in enumerate(integrations):
        y = 216 - index * 22
        c.setFillColor(AMBER)
        c.circle(688, y + 2, 3, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica", 7.7)
        c.drawString(698, y - 1, value)

    # Architecture guardrails.
    label(c, "System guardrails", 34, 135)
    guardrails = [
        ("Secrets", "Database and provider keys stay only in service environment variables."),
        ("Permissions", "Roles are enforced by the API, not only hidden in the user interface."),
        ("Auditability", "Every sensitive admission, fee, and configuration action gains an activity record."),
    ]
    for index, (name, body) in enumerate(guardrails):
        x = 34 + index * 258
        rounded(c, x, 54, 238, 63, white, LINE, 10)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 9.2)
        c.drawString(x + 12, 96, name)
        text_block(c, body, x + 12, 82, 214, size=7.3, leading=9.2, color=MUTED)
    c.showPage()


def data_flow_page(c):
    page_title(c, "Core data architecture and institute workflow", "One source of truth from enquiry to parent communication", 2)
    label(c, "Primary data flow", 34, 498)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(34, 475, "A lead is converted, not copied.")
    text_block(c, "The admissions module creates the starting record. Once confirmed, the same identity becomes the student's permanent institute profile and drives all later operations.", 34, 456, 620, size=8.7, leading=12, color=MUTED)

    steps = [
        ("01", "Lead", "enquiry, source, parent, program interest"),
        ("02", "Follow-up", "calls, notes, counselling, next action"),
        ("03", "Admission", "documents, fee plan, confirmation"),
        ("04", "Student", "profile, parent, enrollment, batch"),
        ("05", "Operations", "attendance, finance, exams, parent updates"),
    ]
    positions = [34, 190, 346, 502, 658]
    for index, ((number, name, body), x) in enumerate(zip(steps, positions)):
        if index < len(steps) - 1:
            arrow(c, x + 126, 347, positions[index + 1] - 12, 347, BLUE)
        rounded(c, x, 299, 126, 96, white, LINE, 10)
        c.setFillColor(BLUE)
        c.circle(x + 18, 371, 11, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(x + 18, 368.5, number)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10.3)
        c.drawString(x + 12, 342, name)
        text_block(c, body, x + 12, 326, 102, size=7.4, leading=9.6, color=MUTED)

    label(c, "Shared data entities", 34, 259)
    data_columns = [
        ("People", ["Users and roles", "Leads", "Students", "Parents"]),
        ("Academic structure", ["Branches", "Courses", "Batches", "Subjects and faculty"]),
        ("Financial and delivery", ["Fee plans", "Invoices and payments", "Class sessions", "Attendance and results"]),
        ("Accountability", ["Follow-ups", "Message logs", "Documents", "Audit logs"]),
    ]
    for index, (name, values) in enumerate(data_columns):
        x = 34 + index * 197
        rounded(c, x, 105, 177, 134, SKY if index % 2 == 0 else PALE, LINE, 10)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(x + 13, 216, name)
        for item_index, value in enumerate(values):
            y = 194 - item_index * 20
            c.setFillColor(BLUE)
            c.circle(x + 17, y + 2, 2.4, fill=1, stroke=0)
            c.setFillColor(INK)
            c.setFont("Helvetica", 7.8)
            c.drawString(x + 26, y - 1, value)

    rounded(c, 34, 54, WIDTH - 68, 34, NAVY, None, 10)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 8.6)
    c.drawString(48, 68, "DATA RULE")
    c.setFont("Helvetica", 8.2)
    c.drawString(111, 68, "Student, parent, batch, and fee details are referenced across modules. They are never recreated in separate tables or separate screens.")
    c.showPage()


def deployment_page(c):
    page_title(c, "Deployment, security, and delivery sequence", "Simple to operate now, ready to extend safely", 3)
    label(c, "Deployment topology", 34, 498)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(34, 475, "A single production service keeps v1 reliable and economical.")

    # Connectors first.
    arrow(c, 195, 355, 273, 355)
    arrow(c, 443, 355, 521, 355)
    arrow(c, 620, 355, 679, 355)
    arrow(c, 358, 305, 358, 247, GREEN)

    box(c, 34, 311, 161, 90, "Users", "Chrome, Safari, Android and iOS browser access. The installed PWA is an optional shell.", BLUE, "implemented")
    box(c, 273, 311, 170, 90, "Render web service", "Builds the repository and runs FastAPI. The service delivers the UI and `/api` endpoints.", BLUE_DARK, "implemented")
    box(c, 521, 311, 99, 90, "API", "Validated requests and modular business logic.", GREEN, "implemented")
    box(c, 679, 311, 128, 90, "Supabase", "Managed PostgreSQL with restricted connection credentials.", GREEN, "implemented")

    rounded(c, 273, 152, 170, 90, GREEN_PALE, GREEN, 11)
    label(c, "Operational controls", 286, 222, GREEN)
    controls = ["Environment secrets", "Database backups", "Error monitoring", "Schema migrations"]
    for index, value in enumerate(controls):
        y = 201 - index * 14
        c.setFillColor(GREEN)
        c.circle(289, y + 2, 2.2, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica", 7.4)
        c.drawString(297, y, value)

    label(c, "Delivery sequence", 34, 133)
    milestones = [
        ("1", "Admissions foundation", "Live leads, follow-ups, counsellor work queue, conversion."),
        ("2", "Student and fee handoff", "Profiles, documents, enrollment, fee plans, invoices, receipts."),
        ("3", "Academic delivery", "Batches, timetable, attendance, faculty, exams, results."),
        ("4", "Parent and automation", "Parent access, WhatsApp/SMS, payment adapter, leadership reports."),
    ]
    for index, (number, name, body) in enumerate(milestones):
        x = 34 + index * 197
        rounded(c, x, 54, 177, 62, white, LINE, 10)
        c.setFillColor(BLUE)
        c.circle(x + 18, 92, 10, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(x + 18, 89.5, number)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 8.6)
        c.drawString(x + 34, 94, name)
        text_block(c, body, x + 12, 78, 153, size=6.7, leading=8.3, color=MUTED)
    c.showPage()


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT), pagesize=landscape(A4))
    pdf.setTitle("Lakshya ERP Technical Architecture")
    pdf.setAuthor("SrS Logics")
    architecture_page(pdf)
    data_flow_page(pdf)
    deployment_page(pdf)
    pdf.save()
    print(OUTPUT)


if __name__ == "__main__":
    main()
