import React from "react";
import Timeline from "@mui/lab/Timeline";
import TimelineItem from "@mui/lab/TimelineItem";
import TimelineSeparator from "@mui/lab/TimelineSeparator";
import TimelineConnector from "@mui/lab/TimelineConnector";
import TimelineContent from "@mui/lab/TimelineContent";
import TimelineDot from "@mui/lab/TimelineDot";
import TimelineOppositeContent from "@mui/lab/TimelineOppositeContent";
import Typography from "@mui/material/Typography";
import { APPLICATION_STATUSES, type ApplicationStatus } from "../lib/types";

const ORDER: ApplicationStatus[] = [
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
];

function indexOf(status: string): number {
  const i = ORDER.indexOf(status as ApplicationStatus);
  return i >= 0 ? i : ORDER.length;
}

interface StatusTimelineProps {
  currentStatus: string;
}

export default function StatusTimeline({ currentStatus }: StatusTimelineProps) {
  const currentIdx = indexOf(currentStatus);
  return (
    <Timeline position="right">
      {ORDER.map((status, idx) => {
        const reached = idx <= currentIdx;
        const isCurrent = status === currentStatus;
        return (
          <TimelineItem key={status}>
            <TimelineOppositeContent color="text.secondary" sx={{ flex: 0.2 }}>
              {reached ? (isCurrent ? "Current" : "Done") : "—"}
            </TimelineOppositeContent>
            <TimelineSeparator>
              <TimelineDot color={reached ? "primary" : "grey"} variant={isCurrent ? "filled" : "outlined"} />
              {idx < ORDER.length - 1 && <TimelineConnector />}
            </TimelineSeparator>
            <TimelineContent>
              <Typography variant="body2" fontWeight={isCurrent ? 600 : 400}>
                {status.replace(/_/g, " ")}
              </Typography>
            </TimelineContent>
          </TimelineItem>
        );
      })}
    </Timeline>
  );
}
