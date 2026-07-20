export const admissionsModuleData = {
  rules: [
    "Every fresh lead should be assigned to a counsellor before the day closes.",
    "Every parent discussion must end with a defined next action and timestamp.",
    "Stage changes should reflect reality, not just optimistic follow-up language.",
    "Won leads should move immediately into onboarding and payment confirmation."
  ],
  kpis: [
    { label: "Hot Leads", value: "18", note: "Need same-day touch" },
    { label: "Demo Booked", value: "27", note: "This week pipeline" },
    { label: "Visit Rate", value: "74%", note: "Parent footfall holding" }
  ],
  stats: [
    { label: "New Leads", value: "186", note: "This month" },
    { label: "Counselling Done", value: "124", note: "66.6% coverage" },
    { label: "Won Admissions", value: "74", note: "39.7% conversion" },
    { label: "Revenue Linked", value: "Rs 18.6L", note: "Confirmed intake" }
  ],
  pipeline: [
    { stage: "Fresh", count: 36, note: "Unassigned or first contact pending", fill: 78 },
    { stage: "Counselling", count: 41, note: "Academic fit and budget discussion", fill: 86 },
    { stage: "Demo Booked", count: 27, note: "Class visit or trial session booked", fill: 68 },
    { stage: "Negotiation", count: 18, note: "Scholarship, urgency, or owner approval", fill: 54 },
    { stage: "Won", count: 74, note: "Admissions confirmed this month", fill: 100 }
  ],
  leadSources: [
    { source: "Website Forms", leads: 42, conversion: "36%" },
    { source: "Seminars in Schools", leads: 51, conversion: "48%" },
    { source: "Parent Referrals", leads: 27, conversion: "63%" },
    { source: "Instagram / Meta Ads", leads: 39, conversion: "28%" },
    { source: "Walk-ins", leads: 27, conversion: "52%" }
  ],
  counsellorLoad: [
    { title: "Priya Kulkarni", note: "32 active leads | 11 hot | 5 parent visits today" },
    { title: "Rahul Wagh", note: "29 active leads | 8 demos booked | 3 pending callbacks" },
    { title: "Kiran Patil", note: "24 active leads | 6 decision-stage cases | strongest win rate" }
  ],
  queue: [
    { title: "Demo confirmations", note: "7 parents need time-slot lock before noon." },
    { title: "Old web leads", note: "8 untouched enquiries should be recycled today." },
    { title: "Scholarship approvals", note: "3 cases waiting on final commercial sign-off." },
    { title: "Walk-in callbacks", note: "5 visitors need brochure and faculty mapping." }
  ],
  checklist: [
    "Course fit, faculty mapping, and batch timing explained clearly",
    "Fee plan, scholarship position, and due date communicated",
    "Demo class or counselling visit scheduled before drop-off risk",
    "Parent concerns logged with next action and responsible owner",
    "Payment intent marked before seat blocking"
  ],
  leads: [
    {
      id: "lead-aarav-thakre",
      student: "Aarav Thakre",
      program: "JEE 11th",
      parent: "Mr. and Mrs. Thakre",
      source: "Website Forms",
      counsellor: "Priya Kulkarni",
      stage: "Hot",
      nextAction: "Parent meeting at 6:30 PM",
      score: "92 / 100 fit score",
      budget: "Rs 1.45L annual plan",
      lastTouch: "Today, 11:20 AM",
      campusVisit: "Scheduled today",
      summary: "High intent family. Student wants faculty mapping, father wants fee clarity and result proof.",
      tasks: [
        "Share JEE faculty roster with results snapshot",
        "Lock counselling room and parent visit checklist",
        "Prepare payment plan comparison before meeting"
      ],
      timeline: [
        "Website form received yesterday at 8:45 PM",
        "Counsellor call completed this morning",
        "Parent visit confirmed for 6:30 PM"
      ]
    },
    {
      id: "lead-saanvi-mohod",
      student: "Saanvi Mohod",
      program: "NEET Repeater",
      parent: "Mrs. Mohod",
      source: "Seminars in Schools",
      counsellor: "Rahul Wagh",
      stage: "Demo Booked",
      nextAction: "Attend biology demo tomorrow",
      score: "88 / 100 fit score",
      budget: "Rs 1.20L full payment",
      lastTouch: "Today, 9:40 AM",
      campusVisit: "Tomorrow, 10:00 AM",
      summary: "Student is already comparing repeaters programs. Demo quality and mentorship clarity will decide the conversion.",
      tasks: [
        "Reserve front-row demo seat",
        "Send NEET repeaters brochure to parent",
        "Schedule post-demo feedback call"
      ],
      timeline: [
        "School seminar lead imported 2 days ago",
        "Counselling call completed yesterday",
        "Biology demo seat confirmed for tomorrow"
      ]
    },
    {
      id: "lead-vedant-zade",
      student: "Vedant Zade",
      program: "MHT-CET",
      parent: "Mr. Zade",
      source: "Instagram / Meta Ads",
      counsellor: "Kiran Patil",
      stage: "Negotiation",
      nextAction: "Owner discount approval",
      score: "84 / 100 fit score",
      budget: "Rs 92K after concession",
      lastTouch: "Today, 1:05 PM",
      campusVisit: "Demo done",
      summary: "Parent is positive after counselling. Discount approval is the only blocker before token payment.",
      tasks: [
        "Share revised fee plan before 4 PM",
        "Get owner approval on concession",
        "Hold Sunday demo seat till payment"
      ],
      timeline: [
        "Instagram lead captured 3 days ago",
        "Demo completed with positive feedback",
        "Concession request raised to owner today"
      ]
    },
    {
      id: "lead-khushi-agrawal",
      student: "Khushi Agrawal",
      program: "Foundation 9-10",
      parent: "Mrs. Agrawal",
      source: "Parent Referrals",
      counsellor: "Priya Kulkarni",
      stage: "Won",
      nextAction: "Admission fee paid",
      score: "95 / 100 fit score",
      budget: "Rs 68K quarterly plan",
      lastTouch: "Yesterday, 7:10 PM",
      campusVisit: "Onboarded",
      summary: "Strong referral conversion. Parent wants orientation, app access, and timetable shared quickly.",
      tasks: [
        "Issue welcome message and ERP login",
        "Share books and orientation schedule",
        "Map student to Foundation 10-A batch"
      ],
      timeline: [
        "Referral enquiry received this week",
        "Parent counselling completed same day",
        "Admission closed and payment received"
      ]
    },
    {
      id: "lead-yash-bisen",
      student: "Yash Bisen",
      program: "NEET 12th",
      parent: "Mr. Bisen",
      source: "Walk-ins",
      counsellor: "Rahul Wagh",
      stage: "Follow-up",
      nextAction: "Share test schedule and fee plan",
      score: "79 / 100 fit score",
      budget: "Rs 1.05L installment plan",
      lastTouch: "Yesterday, 5:30 PM",
      campusVisit: "Walk-in completed",
      summary: "Family liked the institute but needs stronger academic roadmap and flexibility on installments.",
      tasks: [
        "Send test planner by evening",
        "Explain installment structure clearly",
        "Re-open follow-up call tomorrow morning"
      ],
      timeline: [
        "Walk-in captured at reception yesterday",
        "Counsellor discussion completed on-site",
        "Family requested one-day time to compare"
      ]
    }
  ]
};
