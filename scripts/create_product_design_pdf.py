from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


OUTPUT = Path(__file__).resolve().parents[1] / "output" / "pdf" / "lakshya-erp-product-design-specification.pdf"
WIDTH, HEIGHT = landscape(A4)

NAVY = HexColor("#102A43")
INK = HexColor("#243B53")
MUTED = HexColor("#627D98")
BLUE = HexColor("#1476C9")
SKY = HexColor("#EAF4FF")
PALE = HexColor("#F7FAFD")
LINE = HexColor("#D9E2EC")
GREEN = HexColor("#13795B")
GREEN_PALE = HexColor("#E6F5EE")
AMBER = HexColor("#B45309")
AMBER_PALE = HexColor("#FEF3E3")


def wrap(c, text, font, size, max_width):
    words, lines, current = text.split(), [], ""
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


def text(c, value, x, y, width, size=9, leading=12, font="Helvetica", color=INK):
    c.setFillColor(color)
    c.setFont(font, size)
    for line in wrap(c, value, font, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y


def rounded(c, x, y, w, h, fill, stroke=None, radius=12):
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1 if stroke else 0)


def chip(c, value, x, y, fill=SKY, color=BLUE):
    w = stringWidth(value.upper(), "Helvetica-Bold", 7.5) + 20
    rounded(c, x, y, w, 20, fill, None, 10)
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(x + w / 2, y + 6.5, value.upper())


def header(c, title, subtitle, page, total=10):
    c.setFillColor(NAVY)
    c.rect(0, HEIGHT - 68, WIDTH, 68, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 17)
    c.drawString(32, HEIGHT - 39, title)
    c.setFillColor(HexColor("#B9D8F5"))
    c.setFont("Helvetica", 8.7)
    c.drawRightString(WIDTH - 32, HEIGHT - 36, subtitle)
    c.setStrokeColor(LINE)
    c.line(32, 26, WIDTH - 32, 26)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.4)
    c.drawString(32, 13, "Lakshya ERP | Product design specification | SrS Logics")
    c.drawRightString(WIDTH - 32, 13, f"{page} / {total}")


def card(c, x, y, w, h, title, role, sections, tone=BLUE):
    rounded(c, x, y, w, h, white, LINE)
    c.setFillColor(tone)
    c.rect(x, y + h - 6, w, 6, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x + 14, y + h - 28, title)
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 7.1)
    c.drawString(x + 14, y + h - 45, role.upper())
    cursor = y + h - 70
    for heading, body in sections:
        c.setFillColor(tone)
        c.setFont("Helvetica-Bold", 7.3)
        c.drawString(x + 14, cursor, heading.upper())
        cursor = text(c, body, x + 14, cursor - 13, w - 28, size=7.6, leading=9.4, color=INK)
        cursor -= 11


def page_intro(c):
    c.setFillColor(NAVY)
    c.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    c.setFillColor(HexColor("#173E63"))
    c.circle(WIDTH - 115, HEIGHT - 105, 135, fill=1, stroke=0)
    c.setFillColor(HexColor("#176C73"))
    c.circle(WIDTH - 55, 90, 170, fill=1, stroke=0)
    chip(c, "Client review", 48, 466, HexColor("#1B4267"), HexColor("#B9D8F5"))
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 31)
    c.drawString(48, 405, "Lakshya ERP")
    c.setFont("Helvetica", 22)
    c.drawString(48, 371, "Product design specification")
    text(c, "A clear view of what the institute will operate: admissions, student records, academics, finance, inventory, communication and parent access.", 48, 323, 485, size=11, leading=16, color=HexColor("#D9EAF8"))
    rounded(c, 48, 111, 500, 132, HexColor("#173B5A"), None, 16)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(70, 209, "What this document confirms")
    items = [
        "The workspace each team uses and the actions they can perform.",
        "How an enquiry becomes a student and then moves through daily operations.",
        "How the system protects permissions, records history and supports mobile work.",
    ]
    y = 184
    for item in items:
        c.setFillColor(HexColor("#65C5E8"))
        c.circle(74, y + 3, 3, fill=1, stroke=0)
        text(c, item, 87, y, 428, size=9, leading=12, color=HexColor("#D9EAF8"))
        y -= 29
    c.setFillColor(HexColor("#B9D8F5"))
    c.setFont("Helvetica", 8)
    c.drawString(48, 42, "Prepared by SrS Logics for Lakshya Institution")
    c.showPage()


def page_foundation(c):
    header(c, "How the product stays connected", "One source of truth, with a clear workspace for each team", 3)
    chip(c, "Operating model", 32, 494)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 17)
    c.drawString(32, 468, "The ERP follows one connected student journey.")
    text(c, "Teams work in focused modules, while leads, students, guardians, batches and financial records remain shared and consistent across the institute.", 32, 448, 690, size=9, leading=13, color=MUTED)
    steps = [
        ("1", "Enquiry", "Website, walk-in, calls, referrals and campaigns enter one admissions queue."),
        ("2", "Admission", "Counselling, documents, course, batch and fee plan are confirmed."),
        ("3", "Student record", "A single student and guardian profile becomes the operational reference."),
        ("4", "Daily delivery", "Classes, attendance, assignments, payments, messages and inventory activity are connected."),
    ]
    x = 32
    for index, title, body in steps:
        rounded(c, x, 274, 182, 122, PALE, LINE)
        rounded(c, x + 14, 347, 28, 28, BLUE, None, 14)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(x + 28, 356, index)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x + 14, 328, title)
        text(c, body, x + 14, 310, 154, size=7.8, leading=10, color=MUTED)
        if x < 578:
            c.setStrokeColor(BLUE)
            c.setLineWidth(1.4)
            c.line(x + 182, 335, x + 202, 335)
        x += 202
    rounded(c, 32, 72, 776, 153, GREEN_PALE, GREEN)
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(52, 194, "PRODUCT-WIDE DESIGN RULES")
    rules = [
        "One record: modules reference the same student, parent, course and batch instead of creating copies.",
        "Focused workspaces: dashboards summarize performance; queues are used to complete daily work.",
        "Traceable changes: admissions, payments, stock and approvals keep user, date, reason and history.",
        "Mobile-ready: smaller screens use a drawer, compact records, large actions and clear saved/error states.",
    ]
    y = 168
    for rule in rules:
        c.setFillColor(GREEN)
        c.circle(56, y + 3, 2.7, fill=1, stroke=0)
        text(c, rule, 68, y, 700, size=8.4, leading=11, color=INK)
        y -= 22
    c.showPage()


def page_architecture(c):
    header(c, "Lakshya ERP architecture", "How users, workspaces and data connect in the finished product", 2)
    chip(c, "System architecture", 32, 494)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(32, 468, "Every team uses a focused workspace connected to shared institute data.")
    text(c, "The owner sees decisions and exceptions, while operational teams complete their work inside dedicated modules. The same student, batch, finance and stock records move safely across the system.", 32, 448, 710, size=9, leading=13, color=MUTED)

    top = [
        ("Leadership", "Owner / director"),
        ("Operations", "Admissions, accounts, coordinators"),
        ("Learning", "Faculty, students and parents"),
    ]
    for x, (title, body) in zip((32, 292, 552), top):
        rounded(c, x, 356, 224, 52, PALE, LINE)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(x + 13, 385, title)
        text(c, body, x + 13, 370, 194, size=7.7, leading=10, color=MUTED)
        c.setStrokeColor(BLUE)
        c.setLineWidth(1.2)
        c.line(x + 112, 356, x + 112, 332)

    workspaces = [
        (32, "Admissions CRM", "leads, follow-ups, conversion", BLUE),
        (230, "Student + enrollment", "profiles, guardians, batches", GREEN),
        (428, "Academic operations", "timetable, attendance, exams", BLUE),
        (626, "Finance + inventory", "fees, receipts, stock control", AMBER),
    ]
    for x, title, body, tone in workspaces:
        rounded(c, x, 248, 160, 72, white, LINE)
        c.setFillColor(tone)
        c.rect(x, 314, 160, 6, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(x + 12, 287, title)
        text(c, body, x + 12, 271, 136, size=7.1, leading=9, color=MUTED)
        c.setStrokeColor(GREEN)
        c.setLineWidth(1.2)
        c.line(x + 80, 248, x + 80, 220)

    rounded(c, 32, 139, 754, 78, GREEN_PALE, GREEN)
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(52, 185, "SHARED ERP FOUNDATION")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(52, 163, "Student, parent, course, batch, enrollment, user, invoice and stock records")
    text(c, "Role permissions, audit history, validation, mobile behavior and reporting are applied across every workspace.", 52, 146, 650, size=8, leading=10, color=MUTED)

    outputs = [
        ("Parent access", "attendance, receipts, results, assignments"),
        ("Communication", "approved notifications and delivery history"),
        ("Owner reports", "funnel, collections, performance and stock"),
    ]
    for x, (title, body) in zip((32, 294, 556), outputs):
        rounded(c, x, 58, 230, 48, NAVY, None)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 8.6)
        c.drawString(x + 12, 83, title)
        text(c, body, x + 12, 69, 202, size=6.8, leading=8, color=HexColor("#B9D8F5"))
    c.showPage()


def module_page(c, page, title, subtitle, lead, cards, note_title, note, note_tone=GREEN):
    header(c, title, subtitle, page)
    chip(c, "Included design", 32, 494)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(32, 468, lead)
    x_positions = [32, 297, 562]
    for x, data in zip(x_positions, cards):
        card(c, x, 190, 242, 226, *data)
    rounded(c, 32, 79, 772, 76, GREEN_PALE if note_tone == GREEN else SKY, note_tone)
    c.setFillColor(note_tone)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(50, 126, note_title.upper())
    text(c, note, 50, 107, 728, size=8.6, leading=11, color=INK)
    c.showPage()


def create_pdf():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=landscape(A4))
    c.setTitle("Lakshya ERP Product Design Specification")
    c.setAuthor("SrS Logics")
    page_intro(c)
    page_architecture(c)
    page_foundation(c)
    module_page(c, 4, "Admissions CRM", "The first release: a controlled journey from enquiry to confirmed admission", "The team works from an action queue, not a crowded dashboard.", [
        ("Lead intake", "Front desk / counsellor", [("Screen", "Student and guardian details, program interest, source, branch and first note."), ("Actions", "Create lead, check duplicate mobile, assign counsellor and set first follow-up.")], BLUE),
        ("Lead desk", "Counsellor", [("Screen", "Filterable queue by stage, owner, program, source, priority and next action."), ("Actions", "Log calls, write notes, schedule follow-up, change stage and request approval.")], GREEN),
        ("Conversion review", "Admissions manager", [("Screen", "Course, branch, batch, documents, admission date and fee-plan handoff."), ("Actions", "Confirm conversion or keep documents pending with a visible owner.")], AMBER),
    ], "CONTROL", "A lead cannot be converted until the essential guardian, course, branch, admission date and document checks are complete. Conversion creates the student and enrollment draft without re-entering data.")
    module_page(c, 5, "Student records, attendance and finance", "One learner profile connects the daily operations", "The student profile is the shared reference point for staff and parents.", [
        ("Student profile", "Admin / coordinator", [("Screen", "Identity, guardians, enrollment, documents, academics, finance and communication history."), ("Actions", "Edit permitted details, verify document reference, allocate or transfer batch.")], BLUE),
        ("Attendance", "Faculty / coordinator", [("Screen", "Class roster with present, late, absent and exception states."), ("Actions", "Mark register, add reason, submit; authorised corrections keep an audit record.")], GREEN),
        ("Fees and finance", "Accounts", [("Screen", "Fee plan, invoices, receipts, outstanding balance, concessions and payment history."), ("Actions", "Record payment, issue receipt, request/approve a concession or adjustment.")], AMBER),
    ], "HANDOFF", "A confirmed payment updates the student ledger, receipt view, collection reporting and permitted reminder flow. Payments are never deleted; refunds or reversals remain separate traceable entries.")
    module_page(c, 6, "Academic operations and faculty delivery", "Batches connect students, teachers, timetable and learning work", "Teachers publish work only to the batches and subjects they are assigned.", [
        ("Batch workspace", "Faculty / coordinator", [("Screen", "Calendar, active students, subjects, upcoming sessions, assignments, exams and risk signals."), ("Actions", "Open class, review completion and publish permitted learning work.")], BLUE),
        ("Assignments and exams", "Faculty / coordinator", [("Screen", "Assignment title, instructions, due date, student status, marks and weak-topic review."), ("Actions", "Publish, review submissions, enter marks and release results after approval.")], GREEN),
        ("Faculty and timetable", "Coordinator", [("Screen", "Faculty workload, rooms, batch schedule and substitution/conflict review."), ("Actions", "Create, move or publish sessions after room and faculty conflict checks.")], AMBER),
    ], "ASSIGNMENT STORAGE", "The ERP saves assignment details, batch eligibility, due date and student status. Files stay in the institute's controlled external Drive link, avoiding unnecessary Supabase file storage.", BLUE)
    module_page(c, 7, "Inventory and material control", "A separate operational module for institute stock", "Every item is traceable from inward receipt through issue, return or approved adjustment.", [
        ("Stock master", "Storekeeper / admin", [("Screen", "Item code, category, unit, vendor, opening balance, current stock and reorder level."), ("Actions", "Create/edit item, maintain active status and review item history.")], BLUE),
        ("Inward and purchase", "Storekeeper / accounts", [("Screen", "Vendor, invoice reference, item lines, quantity, rate and received date."), ("Actions", "Record full/partial inward and preserve the permanent purchase reference.")], GREEN),
        ("Issue, return and adjustment", "Storekeeper / faculty", [("Screen", "Issue destination, quantity, purpose, batch/student/faculty link and return state."), ("Actions", "Issue/return items; request approved write-off or adjustment with a reason.")], AMBER),
    ], "INVENTORY DATA FLOW", "Inward receipt -> stock balance -> batch or student issue -> low-stock alert -> finance visibility and owner reporting. Negative stock is blocked and each movement records actor, time and reason.")
    module_page(c, 8, "Communication, parent access and reporting", "The right information reaches the right person with context", "Communication is event-led and parents see only their verified linked child records.", [
        ("Communication hub", "Admin / managers", [("Screen", "Templates, approved audience, delivery queue, consent state and delivery history."), ("Actions", "Preview, send/schedule authorised messages and inspect retry/failure state.")], AMBER),
        ("Parent app", "Parent / student", [("Screen", "Attendance, fees, receipts, timetable, assignments, results, notices and requests."), ("Actions", "Open controlled links and submit permitted support or PTM requests.")], GREEN),
        ("Owner reporting", "Owner / director", [("Screen", "Admissions funnel, collections, attendance, academic risk, faculty load and inventory health."), ("Actions", "Drill into role-permitted reports, exceptions and action queues.")], BLUE),
    ], "OPTIONAL ADAPTERS", "WhatsApp, SMS, email and payment gateways can be connected when required. The core ERP works without locking the institute into recurring integration costs.", AMBER)
    module_page(c, 9, "Permissions, mobile behavior and quality", "Production rules built into every module", "The product protects real data while keeping daily staff work clear on laptop and mobile.", [
        ("Role permissions", "All users", [("Screen", "Role, branch scope and record-level access set by system administration."), ("Controls", "Backend validates every action; hidden buttons alone never grant access.")], GREEN),
        ("Mobile and PWA", "All users", [("Screen", "Navigation becomes a drawer; records become compact cards with one next action."), ("Controls", "Large touch areas, visible status, optional offline shell and sync confirmation.")], BLUE),
        ("Quality states", "Every module", [("Screen", "Loading, empty, saved, error, duplicate and permission-denied experiences."), ("Controls", "Readable contrast, keyboard focus, labels, validation and stable layouts.")], AMBER),
    ], "DEFINITION OF READY", "A feature is complete only after the role permission, data validation, desktop/mobile behavior, audit trail, success/error states and handoff to the next module are verified.")
    header(c, "Delivery sequence and acceptance", "Each release adds a connected operational workflow", 10)
    chip(c, "Build plan", 32, 494)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(32, 468, "The product is delivered in practical, testable releases.")
    releases = [
        ("Release 1", "Admissions foundation", "Lead intake, counsellor queue, notes, follow-ups, conversion, approval and audit trail.", BLUE),
        ("Release 2", "Student and finance", "Student profile, enrollment, documents, batch allocation, fees, invoices, receipts and parent-ready records.", GREEN),
        ("Release 3", "Academic and inventory operations", "Timetable, attendance, faculty, assignments with external links, exams, results and inventory controls.", AMBER),
        ("Release 4", "Connected experience", "Parent access, communication journeys, leadership reports, approvals, mobile polish and selected integrations.", BLUE),
    ]
    positions = [(32, 310), (424, 310), (32, 153), (424, 153)]
    for (label_value, title, body, tone), (x, y) in zip(releases, positions):
        rounded(c, x, y, 360, 126, PALE, LINE)
        chip(c, label_value, x + 16, y + 88, SKY if tone == BLUE else (GREEN_PALE if tone == GREEN else AMBER_PALE), tone)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 11.5)
        c.drawString(x + 16, y + 65, title)
        text(c, body, x + 16, y + 45, 326, size=8, leading=10.5, color=MUTED)
    rounded(c, 32, 70, 752, 48, GREEN_PALE, GREEN)
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(50, 97, "ACCEPTANCE FOR EVERY RELEASE")
    text(c, "Role-based access, real data flow, audit history, desktop and mobile checks, loading/empty/error states, and a client walkthrough approval.", 245, 97, 510, size=8.4, leading=11, color=INK)
    c.setStrokeColor(LINE)
    c.line(32, 26, WIDTH - 32, 26)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.4)
    c.drawString(32, 13, "Lakshya ERP | Product design specification | SrS Logics")
    c.drawRightString(WIDTH - 32, 13, "10 / 10")
    c.save()


if __name__ == "__main__":
    create_pdf()
