import React, { useState } from "react";
import Button from "@mui/material/Button";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import { DOC_TYPES, type DocType } from "../lib/types";
import { getApiBase } from "../lib/api";

interface FileUploadProps {
  applicationId: number;
  docType: DocType;
  version?: number;
  onUploaded?: () => void;
}

export default function FileUpload({ applicationId, docType: initialDocType, version, onUploaded }: FileUploadProps) {
  const [docType, setDocType] = useState<string>(initialDocType);
  const [ver, setVer] = useState<string>(version != null ? String(version) : "1");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Select a file");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("aktu_token") : null;
      const base = getApiBase();
      const form = new FormData();
      form.append("file", file);
      const url = `${base}/api/applications/${applicationId}/documents?doc_type=${encodeURIComponent(docType)}&version=${encodeURIComponent(ver)}`;
      const res = await fetch(url, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: form,
      });
      if (!res.ok) {
        const t = await res.text();
        let detail = t;
        try {
          const j = JSON.parse(t);
          detail = j.detail || t;
        } catch {
          //
        }
        throw new Error(detail);
      }
      setFile(null);
      onUploaded?.();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ display: "flex", flexWrap: "wrap", gap: 2, alignItems: "flex-end" }}>
      <FormControl size="small" sx={{ minWidth: 160 }}>
        <InputLabel>Document type</InputLabel>
        <Select
          value={docType}
          label="Document type"
          onChange={(e) => setDocType(e.target.value)}
        >
          {DOC_TYPES.map((d) => (
            <MenuItem key={d} value={d}>
              {d}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <TextField
        size="small"
        label="Version"
        type="number"
        value={ver}
        onChange={(e) => setVer(e.target.value)}
        inputProps={{ min: 1 }}
        sx={{ width: 90 }}
      />
      <Button variant="contained" component="label">
        Choose file
        <input
          type="file"
          hidden
          accept=".pdf,.docx,.xlsx,.png,.jpg,.jpeg"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
      </Button>
      {file && <Typography variant="body2">{file.name}</Typography>}
      <Button type="submit" variant="outlined" disabled={!file || loading}>
        {loading ? "Uploading…" : "Upload"}
      </Button>
      {error && <Typography color="error">{error}</Typography>}
    </Box>
  );
}
