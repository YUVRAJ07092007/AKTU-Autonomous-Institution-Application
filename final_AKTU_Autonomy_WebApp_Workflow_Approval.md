# AKTU Academic Autonomy Online Application System — Workflow & Approval Process

AKTU Academic Autonomy Online Application System
Workflow, Checklist/Fields & Competent Authority Approval Process
(aligned to current practice 2025–26)
This document proposes an end-to-end web-based system for processing Academic Autonomy applications for affiliated institutions. The workflow is aligned to AKTU’s Clause 6.29 requirements while also reflecting current operational practice where UGC/AICTE/Accreditation evidence is a primary scrutiny input.

### 1. Key Design Change (as per current practice)

- UGC Autonomy compliance should be treated as PRIMARY. The system should keep UGC fields ON by default (or mandatory), and should not allow final conferment/closure without recording UGC status/letter details (unless explicitly exempted by policy).
- AKTU Clause 6.29(a) remains the internal checklist for university processing; however, the scrutiny dataset must also capture NAAC/NBA/AICTE compliance and other quality indicators commonly used in 2025–26.

### 2. Stakeholders and Roles


### 2.1 Institution-side

- Institution Admin: creates and fills application, uploads annexures, enters payment and dispatch details, tracks status.
- Authorized Signatory: verifies and performs final e-sign/e-acceptance.

### 2.2 AKTU-side

- Dealing Hand / Case Worker: inward, diary entry, scrutiny, deficiency memo, routing to Registrar.
- Registrar Office: reviews and forwards for approvals; controls meeting notices and committee workflows.
- Competent Authority (PVC/VC/authorized): approves committee formation, approves final decision and tenure.
- Committee Members: review, meeting participation (online/offline/hybrid), MoM editing and e-sign approval.
- Optional reviewers: Accounts / Legal / Examination.

### 2.3 Committee composition option

- Provide a configurable option to include external experts / industry representative / UGC nominee (as applicable) to align with autonomy best practices.

### 3. Application Data: Mandatory Fields (AKTU Core)


### 3.1 Institution Profile (Mandatory)

- Institution name, address, district, principal/authorized signatory details, emailid/whatsapp number.
- AKTU affiliation details: college code, programmes/branches, approved intake, current admissions summary.

### 3.2 Autonomy Request (Mandatory)

- Autonomy requested: Academic Autonomy under AKTU.
- Requested effective academic year/semester.
- Programmes/branches/levels covered.

### 3.3 Clause 6.29(a)(i): Curriculum Variations (Mandatory)

- Programme, semester.
- AKTU course code/title vs proposed course code/title.
- Change type: New / Substitution / Equivalent / Minor update.
- Credits & L-T-P (AKTU vs proposed) and total semester credit parity.
- Justification (gap identification + curriculum evaluation summary).
- OBE/Outcome mapping: CO–PO/PSO reference.
- Implementation readiness: faculty availability + lab/library support mapping.
Mandatory uploads: Annexure–IA + approvals/minutes (BoS/Academic Council/BoG as applicable).

### 3.4 Clause 6.29(a)(ii): Examination Mechanism (Mandatory)

- CIE structure (tests/assignments/lab rubrics/viva) and weightage.
- ESE structure and exam governance controls.
- Paper setting, moderation, confidentiality, question bank policy.
- UFM handling, grievance redressal, revaluation/verification.
- Result processing timeline and reporting/submission to AKTU (where applicable).
Mandatory uploads: Annexure–II + exam SOP/sample formats.

### 3.5 Clause 6.29(a)(iii): Capacity (Mandatory sections + uploads)

- Assets/Infrastructure: built-up, labs, library, ICT (summary). Upload: Annexure–V.
- Faculty: dept-wise strength, cadre ratio, qualifications (PhD %, experience bands). Upload: Annexure–IV.
- Research ecosystem: R&D cell, projects/pubs/patents/consultancy metrics. Upload: Annexure–III.
- Finances: Annexure–VII undertaking + audited proof package (recommended): income–expenditure, balance sheet, fee collection, expenditure and student strength.

### 3.6 Accreditation / Quality Evidence (Mandatory in current scrutiny practice)

- NAAC grade/score and validity (upload certificate).
- NBA accreditation details (programme-wise) and validity (upload).
- Latest AICTE approval letter and compliance summary (upload).
- NIRF rank/band (optional but recommended).

### 3.7 Fee/Payment and Hardcopy Tracking (Mandatory)

- If offline: DD(DD no) + upload proof.
- Hardcopy dispatch/receipt tracking: speed post/consignment no. and AKTU diary/inward number + receipt date (AKTU entry).
- System-generated printable cover sheet to link hardcopy to the online application.

### 4. UGC Autonomy Module (Default ON / Mandatory for closure)


### UGC Policy Toggle (AKTU Admin Level)

The system should provide an AKTU Admin-level policy toggle to control how UGC approval status impacts final decisions:
- Mode A (Strict): The system shall not allow issuance of a final “Granted” decision unless the UGC approval status is recorded.
- Mode B (Parallel): The system may allow an AKTU decision, but shall label it as “Subject to UGC” and auto-generate a UGC recommendation packet.
The UGC module should be enabled by default. The system may allow parallel processing, but final closure/approval should require recording UGC status and (where applicable) the UGC approval letter.

### 4.1 UGC Status Tracking (Fields)

- UGC Autonomy Status: Not Applied / Applied / Under Process / Clarification Sought / Approved / Approved with Conditions / Rejected / Withdrawn.
- UGC Application No. (if under process) and portal reference.
- UGC Approval Letter/Order No., Approval Date, validity/tenure (if applicable).
- Conditions summary (if Approved with Conditions).
- Upload UGC approval letter/order (mandatory when status = Approved/Approved with Conditions).

### 4.2 System enforcement rule

- Allow AKTU scrutiny, committee formation, and MoM preparation in parallel.
- Hold final decision issuance (or mark as ‘Conditional/Deferred’) until UGC letter/status is recorded as per policy.

### 5. End-to-End Workflow (Status Pipeline)


### Stage A: Online Draft → Final Submission (Institution)

1. Institution creates application; fills fields; uploads annexures and quality evidence (NAAC/NBA/AICTE).
1. System validates completeness and generates Application ID + QR cover sheet.
1. Authorized Signatory e-signs and submits. Status: Submitted Online (Pending Hardcopy).

### Stage B: Hardcopy Dispatch / Receipt (Institution → AKTU)

1. Institution enters dispatch details (speed post/consignment number) and uploads proof if available.
1. Dealing Hand records AKTU diary/inward number and receipt date; system issues acknowledgment to institution.
1. Status: Hardcopy Received – Under Scrutiny.

### Stage C: Scrutiny & Deficiency Loop (Dealing Hand)

1. Checklist scrutiny: clause-wise completeness + accreditation/AICTE proofs + fee verification.
1. If deficient: deficiency memo auto-generated with task list and due date. Status: Deficiency Raised.
1. Institution submits corrections; case returns to scrutiny until cleared.
1. Status: Scrutiny Cleared – Ready for Committee Formation.

### Stage D: Approval for Committee Formation (Registrar → Competent Authority)

1. Dealing Hand forwards scrutiny note to Registrar.
1. Registrar forwards proposal for committee constitution to competent authority.
1. Competent authority approves committee composition and scope; status: Approved for Committee Formation.

### Stage E: Office Order Issuance (System Generated)

1. System generates committee formation Office Order with members, scope (Clause 6.29 report), timelines and meeting mode.
1. Competent authority e-signs; Office Order published in case file; members notified.
1. Status: Committee Constituted.

### Stage F: Meeting Notice (Online/Offline/Hybrid)

1. Registrar office schedules meeting; system sends notice via email/whatsapp + calendar invite.
1. Agenda auto-includes Clause 6.29(a)(i)-(iii) review points and UGC/AICTE/Accreditation checks.
1. Status: Meeting Scheduled.

### Stage G: AI/Template-Assisted Draft MoM + Collaborative Finalization

1. System generates a primary MoM using the approved template with clause-wise sections and annexure references.
1. MoM editor supports track changes, comments and version control.
1. Add a clause-wise scoring panel: Yes / Partial / No with mandatory remarks for Partial/No (improves consistency).
1. Chair/Convener finalizes the MoM; members e-sign/approve as per policy.
1. Status: MoM Finalized – Submitted to Competent Authority.

### Stage H: Decision by Competent Authority (PVC/VC)

1. Competent authority reviews the MoM and complete decision packet (application + annexures + scrutiny trail + office order).
1. Decision options: Granted / Granted with Conditions / Deferred / Rejected.
1. Record autonomy tenure: Granted for ____ years (e.g., 5/10) and validity dates.
1. System generates decision letter and sends it to the institution; portal stores signed PDF.
1. Status: Closed (Granted/Conditional/Deferred/Rejected).

### 6. Competent Authority Approval Workflow (Controls)

- Dedicated approval queue for: (i) committee formation, (ii) office order e-sign, (iii) final decision e-sign.
- Each approval stores approver name/designation, timestamp, remarks and digital signature.
- Decision packet is locked post-signature; all versions retained for audit.
- Renewal reminders: auto-notify institution and AKTU 6–12 months before autonomy expiry.

### 7. Payment Module Upgrade

- DD is used: capture DD details and upload scanned DD; record receipt and treasury/account entry by Accounts section.

### 8. Digitization Enhancements (Practical)

- Optional document e-verification via DigiLocker/e-sign to reduce dependence on hardcopy over time.
- Dashboard timeline tracker (PNR-style): shows stage, owner, date entered, pending since and expected SLA days.
- Structured rejection/deferral reasons (dropdown + mandatory remarks) for analytics and transparency.
- Data retention and access policy: define storage period, download permissions, and archival workflow.

### 9. Status Codes

- Draft
- Submitted Online (Pending Hardcopy)
- Hardcopy Received – Under Scrutiny
- Deficiency Raised
- Scrutiny Cleared – Ready for Committee Formation
- Approved for Committee Formation
- Committee Constituted
- Meeting Scheduled
- MoM Draft Generated
- MoM Finalized – Submitted to Competent Authority
- Decision Issued – Closed

### 10. UGC Status Badge (Displayed on Case Header)

- UGC: Not Applied / Under Process / Clarification Sought / Approved / Approved with Conditions / Rejected / Withdrawn
