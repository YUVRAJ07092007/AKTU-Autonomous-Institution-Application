/** Mirrors backend enums/schemas for frontend use. */
export const APPLICATION_STATUSES = [
  "DRAFT",
  "SUBMITTED_ONLINE",
  "HARDCOPY_DISPATCHED",
  "HARDCOPY_RECEIVED",
  "UNDER_SCRUTINY",
  "DEFICIENCY_RAISED",
  "SCRUTINY_CLEARED",
  "COMMITTEE_CONSTITUTED",
  "MEETING_SCHEDULED",
  "MOM_DRAFT_GENERATED",
  "MOM_FINALIZED",
  "DECISION_ISSUED",
  "CLOSED",
] as const;

export type ApplicationStatus = (typeof APPLICATION_STATUSES)[number];

export const DOC_TYPES = [
  "CoverLetter",
  "ApplicationForm",
  "AnnexureIA",
  "AnnexureII",
  "AnnexureIII",
  "AnnexureIV",
  "AnnexureV",
  "AnnexureVII",
  "FeeProof",
  "OfficeOrder",
  "MoM",
  "DecisionLetter",
  "UGCApproval",
  "ACK",
  "MeetingNotice",
] as const;

export type DocType = (typeof DOC_TYPES)[number];

export interface Application {
  id: number;
  public_id: string;
  institution_id: number;
  status: string;
  created_at: string;
  updated_at: string;
  requested_from_year: number;
  programmes_json: Record<string, unknown>;
  ugc_policy_mode: string;
  ugc_approval_recorded?: boolean;
}

export interface DocumentOut {
  id: number;
  application_id: number;
  doc_type: string;
  filename: string;
  uploaded_at: string;
  version: number;
}
