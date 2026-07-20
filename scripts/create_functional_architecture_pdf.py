from pathlib import Path
from math import hypot

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


OUTPUT = Path(__file__).resolve().parents[1] / "output" / "pdf" / "lakshya-erp-functional-architecture.pdf"
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
RED = HexColor("#C2413A")


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


def header(c, title, subtitle, page, total=15):
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
    c.setFont("Helvetica", 7.5)
    c.drawString(32, 13, "Lakshya ERP | Functional architecture derived from the approved product demo | SrS Logics")
    c.drawRightString(WIDTH - 32, 13, f"{page} / {total}")


def arrow(c, x1, y1, x2, y2, color=BLUE, dashed=False):
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.35)
    if dashed:
        c.setDash(4, 3)
    c.line(x1, y1, x2, y2)
    length = hypot(x2 - x1, y2 - y1)
    if length:
        ux, uy = (x2 - x1) / length, (y2 - y1) / length
        back_x, back_y = x2 - ux * 6, y2 - uy * 6
        perp_x, perp_y = -uy * 3, ux * 3
        c.line(x2, y2, back_x + perp_x, back_y + perp_y)
        c.line(x2, y2, back_x - perp_x, back_y - perp_y)
    c.restoreState()


def connector(c, x1, y1, x2, y2, color=BLUE, dashed=False):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(1.35)
    if dashed:
        c.setDash(4, 3)
    c.line(x1, y1, x2, y2)
    c.restoreState()


def module_card(c, x, y, w, h, name, owner, features, writes, feeds, tone=BLUE):
    rounded(c, x, y, w, h, white, LINE, 10)
    c.setFillColor(tone)
    c.rect(x, y + h - 6, w, 6, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x + 12, y + h - 23, name)
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 7.2)
    c.drawString(x + 12, y + h - 38, f"PRIMARY OWNER: {owner.upper()}")

    label(c, "Features", x + 12, y + h - 56, tone)
    feature_y = y + h - 69
    for feature in features:
        c.setFillColor(tone)
        c.circle(x + 15, feature_y + 2, 2, fill=1, stroke=0)
        text_block(c, feature, x + 22, feature_y, w - 34, size=7.2, leading=8.6, color=INK)
        feature_y -= 15

    base_y = y + 23
    c.setStrokeColor(LINE)
    c.line(x + 12, base_y + 33, x + w - 12, base_y + 33)
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 6.8)
    c.drawString(x + 12, base_y + 21, "WRITES")
    text_block(c, writes, x + 49, base_y + 21, w - 61, size=6.8, leading=8, color=MUTED)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 6.8)
    c.drawString(x + 12, base_y + 8, "FEEDS")
    text_block(c, feeds, x + 47, base_y + 8, w - 59, size=6.8, leading=8, color=MUTED)


def architecture_overview(c):
    header(c, "Lakshya ERP - Functional architecture", "How all approved demo modules connect and share data", 1)
    label(c, "System design", 32, 498)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(32, 475, "Every module is connected through shared institute master data.")
    text_block(c, "The application is built as a modular ERP: each team gets its own workspace, while shared lead, learner, batch, finance and stock data keeps operations aligned.", 32, 455, 660, size=8.8, leading=12, color=MUTED)

    # Connectors behind modules.
    arrow(c, 184, 354, 235, 354)
    arrow(c, 371, 354, 422, 354)
    arrow(c, 563, 354, 615, 354)

    label(c, "Journey entry", 32, 410)
    rounded(c, 32, 310, 152, 82, SKY, BLUE, 11)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(44, 365, "Lead sources")
    text_block(c, "Website, walk-in, phone, WhatsApp, Instagram, seminar, referral, campaign", 44, 347, 125, size=7.5, leading=10, color=MUTED)

    label(c, "Admissions", 235, 410)
    rounded(c, 235, 310, 136, 82, white, BLUE, 11)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(247, 365, "Admissions CRM")
    text_block(c, "Lead desk, counselling, follow-ups, conversion, documents", 247, 347, 110, size=7.5, leading=10, color=MUTED)

    label(c, "Central record", 422, 410)
    rounded(c, 422, 289, 141, 103, GREEN_PALE, GREEN, 11)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(434, 350, "Student + enrollment")
    text_block(c, "Student, parent, branch, course, batch, fee plan, access status", 434, 332, 115, size=7.5, leading=10, color=MUTED)

    label(c, "Daily operations", 615, 410)
    rounded(c, 615, 310, 194, 82, white, GREEN, 11)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(627, 365, "Academic and financial operations")
    text_block(c, "Attendance, fees, timetable, exams, results, faculty workload and inventory", 627, 347, 168, size=7.5, leading=10, color=MUTED)

    operation_nodes = [
        (32, "Attendance", "marks, late, absence"),
        (230, "Fees", "plans, dues, receipts"),
        (428, "Academics", "exams, results, action"),
        (626, "Inventory", "stock, issues, reorder"),
    ]
    for x, title, body in operation_nodes:
        rounded(c, x, 139, 160, 61, PALE, LINE, 10)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 9.2)
        c.drawString(x + 12, 177, title)
        text_block(c, body, x + 12, 162, 135, size=7.2, leading=9, color=MUTED)

    outputs = [
        (112, "Communication Hub", "WhatsApp, SMS, notices, logs"),
        (340, "Owner Reports", "funnel, cash flow, stock, performance"),
        (568, "Parent App", "attendance, fees, results, timetable"),
    ]
    for x, title, body in outputs:
        rounded(c, x, 48, 160, 42, NAVY, None, 10)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 8.7)
        c.drawString(x + 12, 70, title)
        c.setFont("Helvetica", 6.7)
        c.setFillColor(HexColor("#B9D8F5"))
        c.drawString(x + 12, 57, body)

    # The daily-operations hub routes shared data through one clean module bus.
    connector(c, 712, 310, 712, 235, GREEN)
    connector(c, 112, 235, 712, 235, GREEN)
    arrow(c, 112, 235, 112, 200, GREEN)
    arrow(c, 310, 235, 310, 200, GREEN)
    arrow(c, 508, 235, 508, 200, GREEN)
    arrow(c, 706, 235, 706, 200, GREEN)
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 7.2)
    c.drawCentredString(WIDTH / 2, 106, "Operations feed family communication, leadership reporting and the parent experience.")
    c.showPage()


def data_journey(c):
    header(c, "How data travels across the ERP", "Approved demo workflow from enquiry through academic delivery", 2)
    label(c, "End-to-end journey", 32, 498)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(32, 475, "The record grows as the student's relationship with Lakshya grows.")
    text_block(c, "Each step adds verified information to the existing record. This stops repeated data entry, makes accountability visible, and allows the owner to see the current state of the institution in one place.", 32, 455, 720, size=8.8, leading=12, color=MUTED)

    journey = [
        ("1", "Enquiry captured", "Lead, parent contact, source, program interest", "Admissions"),
        ("2", "Counselling managed", "Owner, notes, next action, demo or visit, fee discussion", "Admissions"),
        ("3", "Admission confirmed", "Documents, final course, fee plan, payment intent", "Admissions + Accounts"),
        ("4", "Student activated", "Student ID, parent link, enrollment, batch, login", "Student Core"),
        ("5", "Classes delivered", "Timetable, faculty, attendance, assignments, exams", "Academic Operations"),
        ("6", "Family informed", "Receipts, alerts, results, notices, mentor updates", "Communication + Parent"),
    ]
    positions = [(32, 300), (294, 300), (556, 300), (556, 145), (294, 145), (32, 145)]
    for index, (number, title, body, owner) in enumerate(journey):
        x, y = positions[index]
        rounded(c, x, y, 238, 112, white, LINE, 11)
        c.setFillColor(BLUE)
        c.circle(x + 23, y + 83, 13, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x + 23, y + 80, number)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10.4)
        c.drawString(x + 44, y + 79, title)
        text_block(c, body, x + 14, y + 56, 210, size=7.4, leading=9.4, color=MUTED)
        rounded(c, x + 14, y + 14, 90, 16, SKY, None, 8)
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 6.8)
        c.drawCentredString(x + 59, y + 19, owner.upper())

    # Journey connectors are drawn after cards so every arrowhead touches its next step.
    arrow(c, 270, 355, 294, 355, BLUE)
    arrow(c, 532, 355, 556, 355, BLUE)
    arrow(c, 675, 300, 675, 257, BLUE)
    arrow(c, 556, 200, 532, 200, BLUE)
    arrow(c, 294, 200, 270, 200, BLUE)

    label(c, "Cross-module rules", 32, 98)
    rules = [
        ("Lead history stays intact", "A converted lead remains linked to the student profile for source and conversion reporting."),
        ("Batch is the operational spine", "Timetable, faculty assignment, attendance, exams, and batch performance all reference the same batch."),
        ("Events trigger action", "Absence, fee due date, result publication, and lead follow-up can create messages, tasks, and dashboard alerts."),
    ]
    for index, (title, body) in enumerate(rules):
        x = 32 + index * 262
        rounded(c, x, 43, 238, 43, SKY if index != 1 else GREEN_PALE, LINE, 9)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 7.6)
        c.drawString(x + 10, 71, title)
        text_block(c, body, x + 10, 59, 216, size=6.5, leading=8, color=MUTED)
    c.showPage()


def modules_part_one(c):
    header(c, "Module architecture: admissions to fees", "Scope and data handoffs defined from the approved demo", 3)
    label(c, "Modules 01 - 05", 32, 498)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(32, 475, "The first five workspaces establish operational control.")

    module_card(c, 32, 278, 240, 166, "01. Owner Dashboard", "Owner / Director", ["Enrollment base, cash in month, class presence", "Executive priorities, growth funnel, portfolio mix", "Watchlist for dues, faculty load, academic risk"], "Aggregated KPIs and alerts", "Reports, owner approvals, decision queue", BLUE)
    module_card(c, 300, 278, 240, 166, "02. Admissions CRM", "Counsellor / Admissions Manager", ["New lead form with student, parent, source, program and owner", "Stage pipeline, filters, lead desk, notes and next action", "Counselling, demo, negotiation, follow-up and conversion"], "Leads, tasks, notes, follow-ups, source attribution", "Student core, fees, communication, dashboard", BLUE)
    module_card(c, 568, 278, 240, 166, "03. Student Records", "Admin / Academic Coordinator", ["Single student profile with parent, batch, attendance, fee and test snapshot", "Academic action notes and parent preferences", "Documents, enrollment status, student access"], "Students, parents, enrollments, documents", "Attendance, fees, academics, parent app, reports", GREEN)
    module_card(c, 166, 72, 240, 166, "04. Attendance", "Faculty / Coordinator", ["Batch-wise strength, present, late, absent and auto action", "Daily attendance summary and repeat absence review", "Parent alert and mentor escalation triggers"], "Class sessions, attendance marks, absence events", "Student profile, communication, reports", GREEN)
    module_card(c, 434, 72, 240, 166, "05. Fees and Finance", "Accounts", ["Fee plans, total, paid, due and next due date", "Collection versus target, outstanding and recovery visibility", "Concession / scholarship monitoring and receipts"], "Fee plans, invoices, payments, receipts, concessions", "Student profile, communication, owner reports", AMBER)
    c.showPage()


def modules_part_two(c):
    header(c, "Module architecture: academics to administration", "Scope and data handoffs defined from the approved demo", 4)
    label(c, "Modules 06 - 11", 32, 498)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(32, 475, "Academic quality, inventory, communication and leadership share controlled institute data.")

    module_card(c, 32, 278, 240, 166, "06. Academics and Exams", "Academic Coordinator", ["Exam calendar for mock tests, OMR, analytics and parent summary", "Batch average, top score, weak subject and corrective action", "Batch assignments with shared links, due dates and completion tracking"], "Exam schedules, marks, assignments, external links", "Student profile, parent app, communication, reports", BLUE)
    module_card(c, 300, 278, 240, 166, "07. Faculty and Timetable", "Academic Coordinator", ["Faculty subject, batches, hours per week, utilization and next class", "Room / time capacity and timetable health notes", "Faculty assignment publishing for assigned batches"], "Faculty records, subject mapping, timetable, class sessions", "Attendance, academics, parent timetable, reports", GREEN)
    module_card(c, 568, 278, 240, 166, "08. Communication Hub", "Admissions / Admin / Academic Team", ["New-lead, absence, fee-reminder and result journeys", "WhatsApp / SMS broadcast log with delivery and owner", "Templates, escalation rules and communication audit"], "Templates, message jobs, delivery logs, consent", "Lead profile, student profile, reports, parent app", AMBER)
    module_card(c, 32, 72, 240, 166, "09. Reports and Owner Views", "Owner / Admin", ["Admissions tracker, batch occupancy and faculty utilization", "Fee due ageing, inventory status and student performance trends", "Communication audit and monthly executive board"], "Saved report filters and export audit", "Reads all operational modules without duplicating data", BLUE)
    module_card(c, 300, 72, 240, 166, "10. Parent App and Settings", "Parent / System Admin", ["Parent: attendance, fees, results, timetable, homework, doubts and PTM", "Admin: branches, courses, batches, fee plans, roles and campaign mapping", "Audit logs, export permissions, templates and escalation policy"], "Parent access, configuration, role and audit controls", "All modules use controlled master data and permissions", GREEN)
    module_card(c, 568, 72, 240, 166, "11. Inventory", "Storekeeper / Accounts / Admin", ["Stock master, category, unit, vendor and reorder level", "Purchase inward, stock issue, return, adjustment and current balance", "Batch or student material issue with low-stock alerts"], "Items, vendors, movements and issue records", "Finance, academic operations, owner reports", AMBER)
    c.showPage()


def event_matrix(c):
    header(c, "Event architecture: what happens after an action", "The ERP turns operating events into visible next steps", 5)
    label(c, "Automation and handoff map", 32, 498)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(32, 475, "An action in one module creates the correct context in the next module.")

    columns = [32, 177, 326, 490, 664]
    widths = [137, 141, 156, 150, 145]
    headers = ["Event", "Recorded in", "Data created or updated", "Automatically visible to", "Follow-up / output"]
    top = 432
    for x, width, name in zip(columns, widths, headers):
        rounded(c, x, top, width, 27, NAVY, None, 6)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 7.2)
        c.drawString(x + 8, top + 10, name)

    rows = [
        ("New lead submitted", "Admissions CRM", "Lead, parent contact, source, program, owner", "Lead desk, source analytics, counsellor queue", "Acknowledgement + first task"),
        ("Counselling update", "Admissions CRM", "Note, stage, next action, appointment", "Owner queue, follow-up manager", "Reminder until activity is completed"),
        ("Admission confirmed", "Admissions + Accounts", "Student, parent link, enrollment, fee setup", "Student record, batch allocation, owner dashboard", "Welcome message + document checklist"),
        ("Attendance marked absent", "Attendance", "Attendance mark and absence count", "Student profile, mentor queue, parent app", "Parent alert + escalation on repeat absence"),
        ("Payment recorded / due", "Fees and Finance", "Invoice, payment, receipt, remaining balance", "Student profile, accounts dashboard, reports", "Receipt or due reminder"),
        ("Exam results published", "Academics and Exams", "Marks, rank, weak subject, recommended action", "Student profile, parent app, academic dashboard", "Scorecard + intervention plan"),
        ("Timetable changed", "Faculty and Timetable", "Class session, room, faculty, time", "Faculty desk, attendance register, parent app", "Schedule notice if needed"),
        ("Assignment published", "Faculty + Academics", "Batch, assignment, shared link, due date, teacher", "Enrolled students, parent app, academic dashboard", "Batch notice + completion tracking"),
        ("Stock received or issued", "Inventory", "Item, vendor, quantity, issue / return and balance", "Finance, batch material issue, owner reports", "Issue log or low-stock alert"),
    ]
    row_h = 34
    for index, row in enumerate(rows):
        y = top - 7 - (index + 1) * row_h
        fill = SKY if index % 2 == 0 else white
        for x, width in zip(columns, widths):
            c.setFillColor(fill)
            c.setStrokeColor(LINE)
            c.rect(x, y, width, row_h, fill=1, stroke=1)
        for (x, width, value) in zip(columns, widths, row):
            text_block(c, value, x + 7, y + row_h - 12, width - 14, size=6.2, leading=7.3, color=INK if x == columns[0] else MUTED)

    rounded(c, 32, 48, WIDTH - 64, 48, GREEN_PALE, GREEN, 10)
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 8.2)
    c.drawString(45, 78, "DESIGN RULE")
    text_block(c, "Every message, report, alert, task and assignment is linked to its lead, student or batch record. This gives staff context and gives the owner an audit trail instead of scattered WhatsApp conversations and spreadsheets.", 45, 64, WIDTH - 90, size=7.7, leading=10, color=INK)
    c.showPage()


def platform_page(c):
    header(c, "Platform architecture and controlled expansion", "How the product is deployed, protected, and extended", 6)
    label(c, "Application platform", 32, 498)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(32, 475, "One deployed application keeps launch simple. Modular boundaries keep growth safe.")
    text_block(c, "Lakshya ERP begins as a single hosted application: the responsive frontend and FastAPI backend are delivered together, while PostgreSQL stores the protected institute record. External providers connect through adapters when selected.", 32, 455, 710, size=8.8, leading=12, color=MUTED)

    # Connectors first.
    arrow(c, 173, 349, 235, 349)
    arrow(c, 395, 349, 457, 349)
    arrow(c, 617, 349, 679, 349)

    boxes = [
        (32, "Users", "Browser and PWA on desktop, Android and iOS", BLUE),
        (235, "Render service", "Hosts the UI and FastAPI application together", BLUE),
        (457, "API modules", "Admissions, students, finance, inventory, academics, communication", GREEN),
        (679, "Supabase PostgreSQL", "Protected operational and audit data", GREEN),
    ]
    for x, title, body, tone in boxes:
        rounded(c, x, 305, 160 if x != 679 else 130, 86, white, LINE, 10)
        width = 160 if x != 679 else 130
        c.setFillColor(tone)
        c.rect(x, 385, width, 6, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x + 12, 361, title)
        text_block(c, body, x + 12, 343, width - 24, size=7.5, leading=10, color=MUTED)

    rounded(c, 457, 148, 160, 90, GREEN_PALE, GREEN, 10)
    label(c, "Required controls", 470, 214, GREEN)
    controls = ["Environment secrets", "Role permissions", "Audit logs", "Backups and migrations"]
    for index, value in enumerate(controls):
        y = 196 - index * 13
        c.setFillColor(GREEN)
        c.circle(474, y + 2, 2.2, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica", 7.4)
        c.drawString(482, y, value)

    rounded(c, 681, 148, 127, 88, PALE, AMBER, 10)
    label(c, "Optional adapters", 694, 214, AMBER)
    adapters = ["WhatsApp / SMS", "Payment gateway", "Email and external file links"]
    for index, value in enumerate(adapters):
        y = 196 - index * 13
        c.setFillColor(AMBER)
        c.circle(698, y + 2, 2.2, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica", 7.4)
        c.drawString(706, y, value)

    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 7.2)
    c.drawCentredString(537, 252, "Applied to every API module")
    c.drawCentredString(744, 252, "Connected only when selected")

    label(c, "Build sequence", 32, 127)
    phases = [
        ("Phase 1", "Admissions CRM", "Lead capture, counsellor queue, follow-ups, conversion"),
        ("Phase 2", "Student and finance", "Profile, enrollment, documents, fees, invoices, receipts"),
        ("Phase 3", "Academic operations", "Timetable, attendance, faculty, exams, inventory and result analytics"),
        ("Phase 4", "Parent and automation", "Parent access, journeys, payment and leadership reporting"),
    ]
    for index, (phase, title, body) in enumerate(phases):
        x = 32 + index * 197
        rounded(c, x, 48, 177, 63, white, LINE, 10)
        rounded(c, x + 12, 85, 49, 15, SKY, None, 8)
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawCentredString(x + 36.5, 89.5, phase.upper())
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(x + 12, 71, title)
        text_block(c, body, x + 12, 58, 153, size=6.65, leading=8.2, color=MUTED)
    c.showPage()


def software_design_shell(c):
    header(c, "Software design: one shell, role-aware workspaces", "The same disciplined experience for owner, staff, faculty and parents", 7)
    label(c, "Product experience", 32, 498)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(32, 475, "One product shell. One focused job on every screen.")
    text_block(c, "Every role sees the same secure application structure, but only the work, records and actions relevant to that role. This keeps the ERP simple to learn and safe to operate.", 32, 455, 710, size=8.8, leading=12, color=MUTED)

    label(c, "Desktop workspace", 32, 410)
    rounded(c, 32, 172, 744, 220, PALE, LINE, 12)
    rounded(c, 46, 188, 158, 188, NAVY, None, 10)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, 346, "Lakshya ERP")
    c.setFont("Helvetica", 7.4)
    for index, item in enumerate(["Dashboard", "Admissions", "Students", "Attendance", "Fees", "Academics", "Inventory", "Reports"]):
        y = 321 - index * 17
        if item == "Admissions":
            rounded(c, 56, y - 6, 134, 16, HexColor("#1C4C70"), None, 7)
        c.setFillColor(white if item == "Admissions" else HexColor("#B9D8F5"))
        c.drawString(68, y, item)

    rounded(c, 218, 334, 544, 42, white, LINE, 9)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(236, 352, "Admissions CRM")
    c.setFillColor(BLUE)
    rounded(c, 648, 343, 96, 22, BLUE, None, 8)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(696, 351, "CREATE LEAD")

    rounded(c, 218, 280, 544, 42, white, LINE, 9)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.5)
    c.drawString(236, 305, "Search and filters: Program   Stage   Counsellor   Follow-up due")
    rounded(c, 218, 188, 352, 78, white, LINE, 9)
    label(c, "Working list", 232, 246)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(232, 227, "Student / parent")
    c.drawString(393, 227, "Stage")
    c.drawString(478, 227, "Next action")
    c.setStrokeColor(LINE)
    c.line(232, 217, 554, 217)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.2)
    c.drawString(232, 201, "Filtered records with one clear next action")
    rounded(c, 584, 188, 178, 78, SKY, LINE, 9)
    label(c, "Detail panel", 598, 246)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(598, 226, "Selected lead")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.2)
    c.drawString(598, 211, "Timeline, notes, follow-up")
    c.drawString(598, 198, "and conversion actions")

    label(c, "Role design", 32, 130)
    roles = [
        ("Owner", "dashboards, approvals, reports", BLUE),
        ("Admissions", "lead desk, follow-ups, conversion", GREEN),
        ("Faculty", "timetable, attendance, assignments", BLUE),
        ("Accounts / Store", "fees, receipts, inventory", AMBER),
    ]
    for index, (role, body, tone) in enumerate(roles):
        x = 32 + index * 190
        rounded(c, x, 48, 176, 64, white, LINE, 10)
        c.setFillColor(tone)
        c.circle(x + 18, 87, 7, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 9.2)
        c.drawString(x + 32, 83, role)
        text_block(c, body, x + 14, 65, 148, size=7.1, leading=9, color=MUTED)
    c.showPage()


def software_design_patterns(c):
    header(c, "Software design: consistent screens, responsive by default", "Shared components prevent one-off pages and keep staff confident", 8)
    label(c, "Screen design rules", 32, 498)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(32, 475, "The design system makes every module feel like the same product.")
    text_block(c, "Pages use the same spacing, labels, status language, actions and mobile behavior. A dashboard informs; a workspace completes work; a detail view explains one record.", 32, 455, 710, size=8.8, leading=12, color=MUTED)

    patterns = [
        (32, 278, "1. Page header", "Clear title, concise context and one visible primary action.", BLUE),
        (286, 278, "2. Operations table", "Filters above; records in rows; one action per row; mobile becomes compact cards.", GREEN),
        (540, 278, "3. Detail and activity", "Timeline, notes and decisions stay with the selected student, lead or transaction.", AMBER),
        (32, 88, "4. Guided form", "Visible labels, inline validation and grouped steps for longer staff workflows.", BLUE),
        (286, 88, "5. Status and alerts", "Written status plus colour: Paid, Due today, Absent, Confirmed or Draft.", GREEN),
        (540, 88, "6. Mobile and PWA", "Drawer navigation, thumb-friendly actions, compact lists and offline shell support.", AMBER),
    ]
    for x, y, title, body, tone in patterns:
        rounded(c, x, y, 222, 142, white, LINE, 11)
        c.setFillColor(tone)
        c.rect(x, y + 132, 222, 10, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(x + 14, y + 105, title)
        text_block(c, body, x + 14, y + 84, 190, size=8, leading=11, color=MUTED)
        c.setStrokeColor(LINE)
        c.line(x + 14, y + 44, x + 208, y + 44)
        c.setFillColor(tone)
        c.setFont("Helvetica-Bold", 7.2)
        c.drawString(x + 14, y + 26, "SHARED ACROSS ALL MODULES")

    rounded(c, 32, 40, 730, 28, GREEN_PALE, GREEN, 9)
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(46, 51, "QUALITY STANDARD")
    c.setFillColor(INK)
    c.setFont("Helvetica", 7.4)
    c.drawString(152, 51, "Keyboard-friendly, WCAG AA contrast, visible focus states, responsive layouts and clear loading, empty and error states.")
    c.showPage()


def design_card(c, x, y, w, h, title, owner, sections, tone=BLUE):
    rounded(c, x, y, w, h, white, LINE, 11)
    c.setFillColor(tone)
    c.rect(x, y + h - 7, w, 7, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10.2)
    c.drawString(x + 14, y + h - 27, title)
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 6.8)
    c.drawString(x + 14, y + h - 42, owner.upper())
    current_y = y + h - 61
    for section, body in sections:
        c.setFillColor(tone)
        c.setFont("Helvetica-Bold", 6.7)
        c.drawString(x + 14, current_y, section.upper())
        current_y = text_block(c, body, x + 14, current_y - 12, w - 28, size=7.2, leading=9, color=INK) - 7


def detailed_admissions_design(c):
    header(c, "Detailed design: admissions from enquiry to conversion", "A focused workspace for counsellors, managers and front desk", 9)
    label(c, "Admissions module", 32, 498)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(32, 475, "The admissions team works from a queue, not a crowded dashboard.")
    text_block(c, "Each lead has one owner, one next action and a complete visible history. Managers control the pipeline without interrupting counselling work.", 32, 455, 710, size=8.8, leading=12, color=MUTED)
    design_card(c, 32, 190, 228, 218, "Lead intake", "Front desk / counsellor", [
        ("Screen", "Create lead with student, parent, program, source, branch and preferred contact time."),
        ("On save", "Assign counsellor, create first follow-up and record source attribution."),
        ("Validation", "Duplicate phone check, required parent contact and program selection before save."),
    ], BLUE)
    design_card(c, 282, 190, 228, 218, "Lead desk", "Counsellor", [
        ("Screen", "Filterable working list with stage, owner, program, source and next-action filters."),
        ("Detail", "Timeline, call notes, documents, visit schedule, reminders and a visible next action."),
        ("Actions", "Log call, schedule follow-up, change stage, request approval and convert."),
    ], GREEN)
    design_card(c, 532, 190, 228, 218, "Manager control", "Admissions manager", [
        ("Screen", "Pipeline, overdue follow-up queue, source quality and counsellor workload."),
        ("Approvals", "Discount or scholarship requests are visible before financial confirmation."),
        ("Outputs", "Conversion creates a student record, enrollment checklist and fee setup handoff."),
    ], AMBER)
    rounded(c, 32, 80, 728, 66, SKY, BLUE, 10)
    label(c, "Screen states", 48, 122)
    text_block(c, "Empty: invite the team to create the first lead.  Loading: preserve table structure.  Duplicate: suggest the existing record.  Permission denied: show who can approve the next action.", 48, 105, 690, size=7.7, leading=10, color=INK)
    c.showPage()


def detailed_student_finance_design(c):
    header(c, "Detailed design: student record, attendance and finance", "One confirmed admission becomes one operational learner record", 10)
    label(c, "Student operations", 32, 498)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(32, 475, "The student profile is the shared reference point for daily operations.")
    text_block(c, "Staff see only the data needed for their task. The system connects attendance, fees, academics and parent communication without duplicating student information.", 32, 455, 710, size=8.8, leading=12, color=MUTED)
    design_card(c, 32, 190, 228, 218, "Student profile", "Admin / coordinator", [
        ("Screen", "Identity, guardian, enrollment, documents, batch, access status and academic snapshot."),
        ("Tabs", "Overview, attendance, fees, academics, communication history and documents."),
        ("Access", "Staff see role-relevant sections; parents only see their linked child record."),
    ], BLUE)
    design_card(c, 282, 190, 228, 218, "Attendance", "Faculty / coordinator", [
        ("Screen", "Batch register with present, late, absent and exception reasons in one quick action flow."),
        ("Rules", "Repeat absence creates a mentor review and optional parent notification."),
        ("Outputs", "Daily summary, attendance percentage and student history update instantly."),
    ], GREEN)
    design_card(c, 532, 190, 228, 218, "Fees and finance", "Accounts", [
        ("Screen", "Fee plan, invoices, receipt history, outstanding balance, due date and concessions."),
        ("Actions", "Record payment, issue receipt, mark adjustment and request concession approval."),
        ("Outputs", "Student view, parent receipt, due reminder, collection dashboard and audit trail."),
    ], AMBER)
    rounded(c, 32, 80, 728, 66, GREEN_PALE, GREEN, 10)
    label(c, "Data rule", 48, 122, GREEN)
    text_block(c, "Admissions creates the student only once. Attendance, finance and academics attach controlled records to that student and enrollment rather than making independent copies.", 48, 105, 690, size=7.7, leading=10, color=INK)
    c.showPage()


def detailed_academic_inventory_design(c):
    header(c, "Detailed design: academics, faculty and inventory", "Batch is the operational spine for teaching, learning and material control", 11)
    label(c, "Academic operations", 32, 498)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(32, 475, "A batch connects faculty, timetable, learning work, students and materials.")
    text_block(c, "Teachers publish only to their assigned batches. Students see work for their own active batch; coordinators see completion, risk and delivery quality without managing every class manually.", 32, 455, 710, size=8.8, leading=12, color=MUTED)
    design_card(c, 32, 190, 228, 218, "Academics and assignments", "Faculty / coordinator", [
        ("Screen", "Batch calendar, assessments, results, weak-topic action and assignment list."),
        ("Assignment", "Teacher selects assigned batch, adds instructions, external Drive link and due date."),
        ("Tracking", "Eligible students receive the item; teacher sees completion, submission and overdue status."),
    ], BLUE)
    design_card(c, 282, 190, 228, 218, "Faculty and timetable", "Coordinator", [
        ("Screen", "Faculty workload, room capacity, class sessions, next class and substitution requests."),
        ("Rules", "Prevent conflicting rooms or faculty allocations before a timetable is published."),
        ("Outputs", "Faculty workspace, attendance register, parent timetable and schedule notices."),
    ], GREEN)
    design_card(c, 532, 190, 228, 218, "Inventory", "Storekeeper / accounts", [
        ("Screen", "Item master, vendor, current stock, reorder level, inward register and issue register."),
        ("Actions", "Receive stock, issue to batch or student, accept return and record approved adjustment."),
        ("Outputs", "Low-stock alert, batch material history, financial visibility and owner reporting."),
    ], AMBER)
    rounded(c, 32, 80, 728, 66, PALE, LINE, 10)
    label(c, "Storage choice", 48, 122)
    text_block(c, "Assignment files remain in the institute's external Drive. The ERP saves the batch, due date, teacher and controlled file link, keeping Supabase Storage usage low.", 48, 105, 690, size=7.7, leading=10, color=INK)
    c.showPage()


def detailed_channels_reporting_design(c):
    header(c, "Detailed design: communication and parent experience", "Reports and settings keep every decision traceable to the original record", 12)
    label(c, "Connected channels", 32, 498)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(32, 475, "The ERP communicates with context, not scattered messages.")
    text_block(c, "Communication is triggered by approved events and permission rules. Parents receive only their child's information; leadership sees trends and exceptions, not raw operational clutter.", 32, 455, 710, size=8.8, leading=12, color=MUTED)
    design_card(c, 32, 202, 346, 192, "Communication hub", "Admin / admissions / academics", [
        ("Journeys", "New enquiry, attendance absence, fee due, result published, timetable change and assignment notification."),
        ("Controls", "Templates, consent, recipient preview, delivery log, retry state and escalation rules."),
        ("Audit", "Every message records source event, recipient, channel, delivery status and acting user."),
    ], AMBER)
    design_card(c, 414, 202, 346, 192, "Parent app", "Parent", [
        ("Home", "Attendance, fees, receipts, results, timetable, assignments, notices, doubts and PTM requests."),
        ("Privacy", "A parent sees only linked children and only information released by institution permissions."),
        ("Mobile", "Large actions, compact records, download links and optional PWA offline shell."),
    ], GREEN)
    design_card(c, 32, 72, 346, 102, "Reports and owner views", "Owner / director", [
        ("Design", "Executive summary with admissions funnel, collection, attendance, performance, faculty utilization, inventory and watchlist. Detailed reports open only when required."),
    ], BLUE)
    design_card(c, 414, 72, 346, 102, "Settings and audit", "System admin", [
        ("Design", "Branches, programs, batches, fee plans, users, roles, templates and approval rules. Every sensitive change is timestamped and attributable."),
    ], AMBER)
    c.showPage()


def detailed_mobile_quality_design(c):
    header(c, "Detailed design: mobile behavior, security and product quality", "Production rules that keep the ERP reliable as usage grows", 13)
    label(c, "Experience and control", 32, 498)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(32, 475, "The software is designed for real staff work on laptops and phones.")
    text_block(c, "Mobile is not a compressed desktop screen. The interface changes intentionally so primary actions, records and alerts remain clear on smaller devices.", 32, 455, 710, size=8.8, leading=12, color=MUTED)
    design_card(c, 32, 190, 228, 218, "Mobile and PWA", "All roles", [
        ("Navigation", "Sidebar becomes a drawer; page title and primary action remain at the top."),
        ("Records", "Tables become compact cards with the record identity, status and one next action."),
        ("Offline", "Cached application shell opens reliably; data-changing work confirms its sync state."),
    ], BLUE)
    design_card(c, 282, 190, 228, 218, "Permissions and safety", "System admin", [
        ("Access", "Role and record permissions are validated by the backend, not just hidden in the UI."),
        ("Audit", "Admissions, financial, stock and permission changes save user, time and action history."),
        ("Protection", "Secrets remain in deployment settings; browser code never receives database credentials."),
    ], GREEN)
    design_card(c, 532, 190, 228, 218, "Quality states", "Every module", [
        ("Accessibility", "Readable contrast, keyboard operation, labels, focus states and written status labels."),
        ("Reliability", "Loading, empty, error, saved and permission-denied states are designed before launch."),
        ("Performance", "Small data requests, stable layouts and reusable components prevent slow, shifting screens."),
    ], AMBER)
    rounded(c, 32, 80, 728, 66, GREEN_PALE, GREEN, 10)
    label(c, "Definition of ready", 48, 122, GREEN)
    text_block(c, "A feature is ready only when its role permission, desktop and mobile views, validation, empty state, error state, audit behavior and handoff to the next module are verified.", 48, 105, 690, size=7.7, leading=10, color=INK)
    c.showPage()


def design_delivery_sequence(c):
    header(c, "Detailed design: build sequence and acceptance criteria", "Each release adds a complete workflow, not disconnected screens", 14)
    label(c, "Implementation design", 32, 498)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(32, 475, "We build the connected journey in practical, testable releases.")
    text_block(c, "The first release begins with admissions, then expands through the confirmed student journey. Each phase is accepted against the screens, permissions, records and handoffs described in this document.", 32, 455, 710, size=8.8, leading=12, color=MUTED)
    phases = [
        ("Release 1", "Admissions foundation", "Lead intake, counsellor queue, notes, follow-ups, conversion, owner review and audit trail.", BLUE),
        ("Release 2", "Student and finance", "Student profile, batch allocation, documents, fee plan, invoices, receipts and parent-ready records.", GREEN),
        ("Release 3", "Academic operations", "Timetable, faculty, attendance, assessments, assignments with external links, results and inventory controls.", AMBER),
        ("Release 4", "Connected channels", "Parent app, communication journeys, reports, approvals, mobile polish and controlled integrations.", BLUE),
    ]
    for index, (release, title, body, tone) in enumerate(phases):
        x = 32 + (index % 2) * 374
        y = 250 - (index // 2) * 150
        rounded(c, x, y, 354, 122, white, LINE, 11)
        rounded(c, x + 16, y + 82, 68, 18, SKY if tone == BLUE else GREEN_PALE if tone == GREEN else AMBER_PALE, None, 8)
        c.setFillColor(tone)
        c.setFont("Helvetica-Bold", 6.7)
        c.drawCentredString(x + 50, y + 88, release.upper())
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x + 16, y + 62, title)
        text_block(c, body, x + 16, y + 43, 318, size=7.7, leading=10, color=MUTED)
    rounded(c, 32, 48, 728, 30, PALE, LINE, 9)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.4)
    c.drawString(46, 59, "ACCEPTANCE FOR EVERY RELEASE")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.4)
    c.drawString(204, 59, "Role-based access, real data flow, mobile check, audit trail, empty/error states and client walkthrough approval.")
    c.showPage()


def detailed_inventory_design(c):
    header(c, "Detailed design: inventory and material control", "A complete stock workflow connected to batches, finance and leadership reporting", 15)
    label(c, "Inventory module", 32, 498)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(32, 475, "Every item is traceable from inward receipt to issue, return or adjustment.")
    text_block(c, "Inventory is an independent operational module. It prevents stock uncertainty, links teaching materials to batches and gives accounts and owners accurate visibility without manual spreadsheets.", 32, 455, 710, size=8.8, leading=12, color=MUTED)

    design_card(c, 32, 202, 228, 210, "Stock master", "Storekeeper / admin", [
        ("Screen", "Item name, category, unit, vendor, opening balance, reorder level and current stock."),
        ("Controls", "Unique item code, active or inactive state, approved unit of measure and reorder threshold."),
        ("Views", "Stock summary, low-stock list, item history and vendor-wise purchase reference."),
    ], BLUE)
    design_card(c, 282, 202, 228, 210, "Inward and purchase", "Storekeeper / accounts", [
        ("Screen", "Purchase inward register with vendor, invoice reference, item, quantity, rate and received date."),
        ("Actions", "Receive full or partial quantity, attach reference link if needed and record delivery variance."),
        ("Handoff", "Updates stock balance, creates finance visibility and keeps a permanent inward history."),
    ], GREEN)
    design_card(c, 532, 202, 228, 210, "Issue, return and adjustment", "Storekeeper / faculty", [
        ("Screen", "Issue items to a batch, individual student, faculty member or internal department."),
        ("Actions", "Issue, return, write-off or request approved adjustment with a reason and quantity."),
        ("Controls", "Block negative stock, show available quantity and require approval for manual adjustments."),
    ], AMBER)

    rounded(c, 32, 80, 728, 88, GREEN_PALE, GREEN, 10)
    label(c, "Inventory data flow", 48, 142, GREEN)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 8.2)
    c.drawString(48, 121, "Inward receipt  →  Stock balance  →  Batch or student issue  →  Low-stock alert  →  Finance and owner reports")
    text_block(c, "Every movement saves item, quantity, source or destination, acting user, time and reason. The batch issue history gives academic teams context; collection and purchase visibility supports finance; the owner sees exceptions and inventory health.", 48, 104, 684, size=7.4, leading=10, color=INK)
    c.showPage()


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT), pagesize=landscape(A4))
    pdf.setTitle("Lakshya ERP Functional Architecture")
    pdf.setAuthor("SrS Logics")
    architecture_overview(pdf)
    data_journey(pdf)
    modules_part_one(pdf)
    modules_part_two(pdf)
    event_matrix(pdf)
    platform_page(pdf)
    software_design_shell(pdf)
    software_design_patterns(pdf)
    detailed_admissions_design(pdf)
    detailed_student_finance_design(pdf)
    detailed_academic_inventory_design(pdf)
    detailed_channels_reporting_design(pdf)
    detailed_mobile_quality_design(pdf)
    design_delivery_sequence(pdf)
    detailed_inventory_design(pdf)
    pdf.save()
    print(OUTPUT)


if __name__ == "__main__":
    main()
