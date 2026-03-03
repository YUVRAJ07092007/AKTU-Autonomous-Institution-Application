import React from "react";
import { useRouter } from "next/router";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import Link from "next/link";
import { useAuth } from "../contexts/AuthContext";

const publicPaths = ["/login", "/"];

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const isPublic = publicPaths.some((p) => router.pathname === p || router.pathname.startsWith(p + "?"));

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <Typography>Loading…</Typography>
      </Box>
    );
  }

  if (isPublic) {
    return <>{children}</>;
  }

  if (!user) {
    if (typeof window !== "undefined") router.replace("/login");
    return null;
  }

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Link href="/dashboard" style={{ flexGrow: 1, textDecoration: "none", color: "inherit" }}>
          <Typography variant="h6" component="span">AKTU Autonomy</Typography>
        </Link>
          <Typography variant="body2" sx={{ mr: 2 }}>
            {user.name} ({user.role})
          </Typography>
          <Button color="inherit" onClick={logout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>
      <Box component="main" sx={{ p: 2 }}>
        {children}
      </Box>
    </>
  );
}
