# Lakshya ERP: Product Design System

## Design direction

The product should feel calm, disciplined, and operational. It is not a marketing dashboard and it should never make staff hunt through decorative cards for an action.

The visual language uses a refined ink-blue base with a clear blue action colour, clean white surfaces, and limited semantic status colours. One page has one primary job.

## Experience rules

1. **One workspace, one job.** Admissions overview shows the pipeline; Lead Desk shows leads; New Lead shows the form. Do not place all three on one screen.
2. **A real action is always visible.** Every operating page has one clear primary action, for example `Create lead`, `Mark attendance`, or `Record payment`.
3. **Important information is earned.** Show the summary first; open full histories, notes, and activity in a detail panel or dedicated page.
4. **Tables are for operations.** Use cards only for summaries, not for rows of comparable records.
5. **Mobile is a first-class interface.** The navigation becomes a drawer; lists become compact cards; primary actions remain within thumb reach.

## Tokens

### Colour

| Token | Value | Use |
| --- | --- | --- |
| `--color-ink-950` | `#102A43` | headings, primary text, dark navigation |
| `--color-ink-700` | `#334E68` | secondary headings, icons |
| `--color-slate-500` | `#627D98` | helper text, table metadata |
| `--color-canvas` | `#F4F8FC` | application background |
| `--color-surface` | `#FFFFFF` | main panels and forms |
| `--color-surface-muted` | `#EEF4FA` | grouped areas and table headers |
| `--color-line` | `#D9E2EC` | dividers and input borders |
| `--color-action` | `#1677C8` | primary buttons, selected navigation, links |
| `--color-action-hover` | `#0B5FA5` | active and hover states |
| `--color-success` | `#13795B` | paid, confirmed, present, completed |
| `--color-warning` | `#B45309` | needs attention, pending follow-up |
| `--color-danger` | `#C2413A` | overdue, failed, destructive actions |

### Typography

Use `Manrope` for the full application UI. It remains readable in tables and on mobile. Use `Space Grotesk` only for short product headings and never for body copy or data tables.

| Token | Value | Use |
| --- | --- | --- |
| `--font-ui` | `Manrope, sans-serif` | forms, tables, body, navigation |
| `--font-display` | `Space Grotesk, sans-serif` | page headings only |
| `--text-xs` | `12px / 18px` | metadata, labels |
| `--text-sm` | `14px / 20px` | helper text, dense tables |
| `--text-base` | `16px / 24px` | default body text |
| `--text-lg` | `20px / 28px` | panel title |
| `--text-xl` | `28px / 34px` | page title |
| `--text-2xl` | `36px / 42px` | desktop page title only |

### Spacing and shape

| Token | Value | Use |
| --- | --- | --- |
| `--space-1` | `4px` | icon gap |
| `--space-2` | `8px` | tight label gap |
| `--space-3` | `12px` | input groups |
| `--space-4` | `16px` | component padding |
| `--space-5` | `20px` | card padding |
| `--space-6` | `24px` | panel padding |
| `--space-8` | `32px` | section gap |
| `--radius-control` | `10px` | inputs and buttons |
| `--radius-panel` | `16px` | cards and panels |

## Application layout

```text
Desktop
┌───────────────┬───────────────────────────────────────────────┐
│ Product logo  │ Page title                     Account / Help │
│ Navigation    ├───────────────────────────────────────────────┤
│               │ Context / filters           Primary action    │
│ Admissions    ├───────────────────────────────────────────────┤
│ Students      │                                               │
│ Attendance    │              Working area                     │
│ Fees          │      table, form, detail, or task queue       │
│ ...           │                                               │
└───────────────┴───────────────────────────────────────────────┘

Mobile
┌─────────────────────────────────────┐
│ Menu   Page title          Account   │
├─────────────────────────────────────┤
│ Context / filter                      │
│ Primary action                        │
├─────────────────────────────────────┤
│ Focused working area                  │
└─────────────────────────────────────┘
```

## Core component specifications

### Page header

- Page title: one line wherever possible.
- Supporting text: one concise sentence, optional.
- Right side: primary action first, then secondary actions.
- Do not repeat the global dashboard hero on module pages.

### Buttons

| Type | Use | Visual treatment |
| --- | --- | --- |
| Primary | the main next action | blue fill, white text |
| Secondary | safe alternate action | white surface, ink border |
| Quiet | low-priority controls | text/icon only |
| Danger | irreversible action | red outline until confirmation |

Minimum touch area is `44 x 44px`. Buttons always have visible hover, focus, disabled, and loading states.

### Forms

- A form is grouped into logical sections with clear labels.
- Labels remain visible above inputs; placeholders never replace labels.
- Required fields show a textual error near the field.
- Save actions stay visible near the bottom on mobile.
- Long forms use steps: `Lead details`, `Academic interest`, `Assignment`, `Review`.

### Data tables

- First column identifies the record, for example student name or invoice number.
- Last column holds actions.
- Filters stay above the table and selected filters remain visible.
- On mobile, each table row becomes a compact record card with only essential fields and one action.
- Never allow horizontal overflow without an intentional compact/mobile view.

### Statuses

Use a label plus colour, never colour alone.

| Status type | Example |
| --- | --- |
| Success | `Paid`, `Present`, `Confirmed`, `Converted` |
| Warning | `Due today`, `Follow-up due`, `Documents pending` |
| Danger | `Overdue`, `Absent`, `Payment failed` |
| Neutral | `Draft`, `Not started`, `No action required` |

## Admission module screen design

### Admissions overview

Purpose: manager control in under 30 seconds.

- Top: four small KPIs: new today, follow-ups due, hot leads, converted this month.
- Middle: stage funnel and overdue follow-up queue.
- Bottom: source performance and counsellor performance.
- Primary action: `Create lead`.

### Lead desk

Purpose: counsellor execution.

- Left/primary: filterable lead table.
- Right/detail: selected lead profile, timeline, next action, quick note.
- Quick actions: `Log call`, `Schedule follow-up`, `Change stage`, `Convert`.
- Do not show broad institute analytics here.

### New lead

Purpose: intake in less than two minutes.

- Guided, two-column desktop form and single-column mobile form.
- Autofill source, counsellor, program and branch from configuration.
- On save: create lead, assign owner, generate first follow-up, confirm the next action.

## Accessibility baseline

- Contrast meets WCAG AA for text and interactive states.
- All actions work with keyboard and show a visible focus state.
- Inputs have associated labels and meaningful error messages.
- Status badges include written status, not just a dot.
- Screen-reader announcements confirm saved changes and form errors.
- Motion is reduced when the device requests reduced motion.

## Quality gate before a screen ships

- It has a specific user and a single primary job.
- Desktop, tablet, and 360px mobile layouts have been checked.
- Empty, loading, error, success, and permission-denied states exist.
- No content is hidden only by colour or hover.
- API loading does not shift the page dramatically.
- A keyboard user can operate all core actions.
- The screen uses these tokens and shared components, not new one-off colours or spacing.
