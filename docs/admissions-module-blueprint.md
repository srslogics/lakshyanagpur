# Admissions Module Blueprint

## Objective

Build the first production module for Lakshya Institution around the admissions journey, from first enquiry to converted student record.

This module should help the institution:

- capture every incoming lead
- track lead source and counsellor activity
- manage follow-ups without leakage
- move serious enquiries toward counselling and admission
- convert confirmed leads into student records cleanly

## Core Outcome

The admissions team should be able to answer these questions at any time:

- How many fresh enquiries came in today?
- Which counsellor owns which lead?
- Which follow-ups are due today?
- Which leads are hot, cold, lost, or converted?
- Which campaigns or sources are bringing good leads?
- How many admissions are pending because of documents, counselling, or fees?

## User Roles

### Owner / Director

- view admissions dashboard
- see source-wise and counsellor-wise performance
- track conversion numbers
- monitor pending follow-ups and lost leads
- approve discounts or special notes if needed

### Admissions Counsellor

- create and update leads
- add call notes and counselling notes
- schedule follow-ups
- update pipeline stage
- mark lead converted or lost

### Front Desk / Admin

- create walk-in enquiries
- upload documents
- assign leads to counsellors
- verify basic details

### Accounts Team

- view admitted leads ready for fee processing
- update admission payment status if connected later

## Main Screens

### 1. Admissions Dashboard

Purpose:
Give daily control over the pipeline.

Widgets:

- new leads today
- follow-ups due today
- total active leads
- converted this month
- lost this month
- walk-ins today
- hot leads
- pending documents

Charts / tables:

- source-wise leads
- counsellor-wise conversions
- stage funnel
- overdue follow-ups list

### 2. Lead List Page

Purpose:
Main operating screen for the admissions team.

Columns:

- lead ID
- student name
- parent name
- mobile number
- course / program
- source
- assigned counsellor
- current stage
- next follow-up date
- priority
- last contact date

Filters:

- date range
- source
- stage
- counsellor
- course
- hot / warm / cold
- follow-up due / overdue

Actions:

- add lead
- assign counsellor
- change stage
- add note
- schedule follow-up
- mark converted
- mark lost

### 3. Lead Detail Page

Purpose:
Single full view of one enquiry.

Sections:

- basic lead information
- student details
- parent / guardian details
- academic interest
- source and campaign details
- counselling notes
- follow-up timeline
- document checklist
- fee / scholarship discussion notes
- conversion status

Quick actions:

- call logged
- WhatsApp sent
- follow-up scheduled
- counselling completed
- documents received
- converted to student
- marked lost

### 4. New Lead Entry Form

Lead sources:

- website enquiry
- walk-in
- phone call
- WhatsApp
- Instagram
- Facebook
- referral
- campaign
- seminar / event
- existing parent referral

Fields:

- enquiry date
- student full name
- student mobile
- parent / guardian name
- parent mobile
- alternate number
- email
- city / area
- class / current standard
- school / college name
- interested course
- target exam
- preferred branch
- source
- campaign name
- assigned counsellor
- priority
- first note

### 5. Follow-up Manager

Purpose:
Prevent enquiry leakage.

Views:

- due today
- overdue
- upcoming
- completed

Each follow-up should include:

- date and time
- contact mode
- purpose
- note after completion
- next action

### 6. Counsellor Workspace

Purpose:
Personal working screen for each counsellor.

Shows:

- assigned leads
- today’s follow-ups
- overdue follow-ups
- hot leads
- recent notes
- monthly conversions

### 7. Conversion Screen

Purpose:
Move a confirmed lead into the student system without duplicate data entry.

Process:

- verify lead details
- confirm course / batch
- confirm branch
- confirm fee plan
- capture admission date
- mark documents received
- create student profile
- hand over to fee / batch / student modules

## Lead Pipeline Stages

Recommended pipeline:

1. New Enquiry
2. Contact Attempted
3. Contacted
4. Follow-up Scheduled
5. Counselling Planned
6. Counselling Done
7. Interested
8. Documents Pending
9. Admission Confirmed
10. Converted
11. Lost
12. Not Interested

## Priority Model

- Hot: likely to convert soon
- Warm: active but needs follow-up
- Cold: low response or long gap

Auto flags:

- overdue follow-up
- no contact in last 3 days
- documents pending after counselling
- fee discussion pending

## Key Data Fields

### Lead Master

- lead_id
- enquiry_date
- first_name
- last_name
- student_name_display
- student_mobile
- parent_name
- parent_mobile
- alternate_mobile
- email
- gender
- date_of_birth
- current_class
- school_name
- city
- area
- preferred_branch
- interested_course
- target_exam
- source
- source_detail
- campaign_name
- assigned_counsellor_id
- stage
- priority
- status
- last_contact_at
- next_followup_at
- converted_at
- lost_reason
- remarks

### Follow-up Table

- followup_id
- lead_id
- counsellor_id
- scheduled_at
- mode
- purpose
- note
- outcome
- next_action
- completed_at
- status

### Counselling Notes

- note_id
- lead_id
- created_by
- note_type
- content
- created_at

### Document Checklist

- doc_id
- lead_id
- document_type
- received
- verified
- uploaded_file
- remarks

## Suggested Document Checklist

- student photo
- Aadhaar / ID proof
- school ID
- previous marksheet
- address proof
- parent ID
- transfer certificate if required
- passport photo set

## Lost Lead Reasons

- no response
- joined competitor
- not interested
- price issue
- distance / location issue
- timing mismatch
- parent declined
- exam goal changed
- duplicate lead

## Dashboard Metrics

Daily:

- leads created today
- leads assigned today
- follow-ups due today
- overdue follow-ups
- walk-ins today

Weekly / monthly:

- total enquiries
- stage-wise count
- conversions
- conversion rate
- lost leads
- source-wise conversion
- counsellor-wise conversion

## Notifications and Reminders

- follow-up due in 1 hour
- overdue follow-up alert
- hot lead not contacted
- documents pending after counselling
- conversion pending after admission confirmation

## Permissions

### Owner

- full view
- reporting
- discount approval
- edit all records

### Admissions Manager

- assign leads
- edit team leads
- monitor follow-ups
- update stage

### Counsellor

- edit only assigned leads
- add notes
- schedule follow-ups
- mark outcomes

### Front Desk

- create leads
- upload documents
- basic updates only

## Integrations for Later Phase

- WhatsApp messaging
- SMS alerts
- website enquiry form sync
- campaign source tagging
- fee module sync
- student record auto-creation

## Build Order

### Phase 1

- lead entry form
- lead list
- lead detail page
- stage change

### Phase 2

- follow-up manager
- counsellor workspace
- notes and timeline

### Phase 3

- conversion flow
- document checklist
- dashboard reporting

### Phase 4

- source analytics
- reminders
- communication integration

## UI Notes

- keep the list page fast and filter-heavy
- keep colours status-driven
- make hot leads visually obvious
- show overdue follow-ups in red
- reduce typing effort using dropdowns and templates
- keep the lead detail page timeline-based and easy to scan

## Recommended First Delivery Scope

For the very first working version, build:

- dashboard
- add lead
- lead list with filters
- lead detail page
- follow-up scheduler
- counsellor assignment
- stage movement
- converted / lost actions

This is enough to make the admissions team operational from day one.

## Final Definition

Admissions Module = enquiry capture + counsellor workflow + follow-up control + conversion tracking.

If this module is strong, the rest of the ERP becomes easier because student records, fees, batches, and parent communication can all begin from clean admissions data.
