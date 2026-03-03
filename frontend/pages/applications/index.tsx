import React, { useEffect, useState } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import Link from "next/link";
import { apiFetch } from "../../lib/api";
import { useAuth } from "../../contexts/AuthContext";
import type { Application } from "../../lib/types";

export default function ApplicationsListPage() {
  const { user } = useAuth();
  const [apps, setApps] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Application[]>("/api/applications")
      .then(setApps)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Typography>Loading applications…</Typography>;
  if (error) return <Typography color="error">{error}</Typography>;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Applications</Typography>
        {user?.role === "INSTITUTION" && (
          <Button component={Link} href="/applications/new" variant="contained">
            New application
          </Button>
        )}
      </Box>
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Public ID</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Year</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {apps.map((app) => (
              <TableRow key={app.id}>
                <TableCell>{app.id}</TableCell>
                <TableCell>{app.public_id}</TableCell>
                <TableCell>{app.status.replace(/_/g, " ")}</TableCell>
                <TableCell>{app.requested_from_year}</TableCell>
                <TableCell align="right">
                  <Button component={Link} href={`/applications/${app.id}`} size="small">
                    Open
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      {apps.length === 0 && (
        <Typography color="text.secondary" sx={{ mt: 2 }}>
          No applications yet.
        </Typography>
      )}
    </Box>
  );
}
