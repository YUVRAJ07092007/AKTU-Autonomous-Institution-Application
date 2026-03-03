import React from "react";
import { useRouter } from "next/router";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardActions from "@mui/material/CardActions";
import Grid from "@mui/material/Grid";
import Link from "next/link";
import { useAuth } from "../../contexts/AuthContext";

export default function DashboardPage() {
  const { user } = useAuth();
  const router = useRouter();

  if (!user) return null;

  const role = user.role;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard — {user.name}
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Role: {role}
      </Typography>

      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Applications</Typography>
              <Typography variant="body2" color="text.secondary">
                List and manage applications
              </Typography>
            </CardContent>
            <CardActions>
              <Button component={Link} href="/applications" size="small">
                View list
              </Button>
              {(role === "INSTITUTION") && (
                <Button component={Link} href="/applications/new" size="small">
                  New application
                </Button>
              )}
            </CardActions>
          </Card>
        </Grid>

        {role === "DEALING_HAND" && (
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6">Dealing hand</Typography>
                <Typography variant="body2" color="text.secondary">
                  Receive hardcopy, scrutiny, deficiency, clear scrutiny
                </Typography>
              </CardContent>
              <CardActions>
                <Button component={Link} href="/applications" size="small">
                  Open applications
                </Button>
              </CardActions>
            </Card>
          </Grid>
        )}

        {role === "REGISTRAR" && (
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6">Registrar</Typography>
                <Typography variant="body2" color="text.secondary">
                  Form committee, schedule meetings, start MoM draft
                </Typography>
              </CardContent>
              <CardActions>
                <Button component={Link} href="/applications" size="small">
                  Open applications
                </Button>
              </CardActions>
            </Card>
          </Grid>
        )}

        {role === "COMMITTEE" && (
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6">Committee</Typography>
                <Typography variant="body2" color="text.secondary">
                  View documents, edit MoM, finalize
                </Typography>
              </CardContent>
              <CardActions>
                <Button component={Link} href="/applications" size="small">
                  Open applications
                </Button>
              </CardActions>
            </Card>
          </Grid>
        )}

        {role === "AUTHORITY" && (
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6">Authority</Typography>
                <Typography variant="body2" color="text.secondary">
                  Approve committee, issue decision
                </Typography>
              </CardContent>
              <CardActions>
                <Button component={Link} href="/applications" size="small">
                  Open applications
                </Button>
              </CardActions>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}
