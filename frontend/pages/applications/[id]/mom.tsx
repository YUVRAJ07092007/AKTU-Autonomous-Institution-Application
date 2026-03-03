/**
 * MoM editor — section-by-section editing (Clause 6.29(a)(i)-(iii)) + comments.
 * Requires COMMITTEE role for edit/finalize; REGISTRAR/AUTHORITY can view.
 * Set NEXT_PUBLIC_API_BASE_URL and use login to get token (or pass via env for dev).
 */
import { useRouter } from "next/router";
import { useState, useEffect, useCallback } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

type MomContent = {
  application_id: number;
  version: number;
  content_json: {
    section_6_29_a_i?: string;
    section_6_29_a_ii?: string;
    section_6_29_a_iii?: string;
    comments?: string;
  };
  updated_by: number;
  updated_at: string;
};

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("aktu_token");
}

function apiHeaders(): HeadersInit {
  const token = getToken();
  const h: HeadersInit = { "Content-Type": "application/json" };
  if (token) (h as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  return h;
}

export default function MomEditorPage() {
  const router = useRouter();
  const id = router.query.id as string | undefined;
  const appId = id ? parseInt(id, 10) : NaN;
  const [content, setContent] = useState<MomContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [finalizing, setFinalizing] = useState(false);
  const [sectionI, setSectionI] = useState("");
  const [sectionII, setSectionII] = useState("");
  const [sectionIII, setSectionIII] = useState("");
  const [comments, setComments] = useState("");

  const loadContent = useCallback(async () => {
    if (!appId || isNaN(appId)) return;
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(`${API_BASE}/api/applications/${appId}/mom/content`, {
        headers: apiHeaders(),
      });
      if (r.status === 404) {
        setContent(null);
        setError("No MoM content yet. Generate draft first (POST /mom/draft).");
        setLoading(false);
        return;
      }
      if (!r.ok) {
        const t = await r.text();
        throw new Error(t || `HTTP ${r.status}`);
      }
      const data: MomContent = await r.json();
      setContent(data);
      const c = data.content_json || {};
      setSectionI(c.section_6_29_a_i ?? "");
      setSectionII(c.section_6_29_a_ii ?? "");
      setSectionIII(c.section_6_29_a_iii ?? "");
      setComments(c.comments ?? "");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load MoM content");
      setContent(null);
    } finally {
      setLoading(false);
    }
  }, [appId]);

  useEffect(() => {
    if (appId && !isNaN(appId)) loadContent();
  }, [appId, loadContent]);

  const handleSave = async () => {
    if (!appId || isNaN(appId)) return;
    setSaving(true);
    setError(null);
    try {
      const r = await fetch(`${API_BASE}/api/applications/${appId}/mom/content`, {
        method: "PUT",
        headers: apiHeaders(),
        body: JSON.stringify({
          section_6_29_a_i: sectionI,
          section_6_29_a_ii: sectionII,
          section_6_29_a_iii: sectionIII,
          comments,
        }),
      });
      if (!r.ok) {
        const t = await r.text();
        throw new Error(t || `HTTP ${r.status}`);
      }
      const data: MomContent = await r.json();
      setContent(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const handleFinalize = async () => {
    if (!appId || isNaN(appId)) return;
    setFinalizing(true);
    setError(null);
    try {
      const r = await fetch(`${API_BASE}/api/applications/${appId}/mom/finalize`, {
        method: "POST",
        headers: apiHeaders(),
      });
      if (!r.ok) {
        const t = await r.text();
        throw new Error(t || `HTTP ${r.status}`);
      }
      setError(null);
      alert("MoM finalized. Status set to MOM_FINALIZED.");
      await loadContent();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Finalize failed");
    } finally {
      setFinalizing(false);
    }
  };

  if (typeof id === "undefined" || !id) {
    return (
      <main style={{ padding: "2rem", fontFamily: "system-ui" }}>
        <h1>MoM Editor</h1>
        <p>Open with application ID, e.g. /applications/1/mom</p>
      </main>
    );
  }

  return (
    <main
      style={{
        maxWidth: 720,
        margin: "0 auto",
        padding: "2rem",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <h1>MoM Editor — Application {appId}</h1>
      <p style={{ color: "#64748b", marginBottom: "1rem" }}>
        Clause 6.29(a)(i)–(iii). Save updates version; Finalize renders DOCX and sets status to MOM_FINALIZED.
      </p>
      {content && (
        <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
          Version {content.version} · last updated {new Date(content.updated_at).toLocaleString()}
        </p>
      )}
      {error && (
        <div
          style={{
            background: "#fef2f2",
            color: "#b91c1c",
            padding: "0.75rem 1rem",
            borderRadius: 8,
            marginBottom: "1rem",
          }}
        >
          {error}
        </div>
      )}
      {loading ? (
        <p>Loading…</p>
      ) : !content ? (
        <p>No MoM content. Generate draft via API: POST /api/applications/{appId}/mom/draft (COMMITTEE only).</p>
      ) : (
        <>
          <section style={{ marginBottom: "1.5rem" }}>
            <label style={{ display: "block", fontWeight: 600, marginBottom: 0.25 }}>6.29(a)(i) — Summary of presentation by institution</label>
            <textarea
              value={sectionI}
              onChange={(e) => setSectionI(e.target.value)}
              rows={4}
              style={{ width: "100%", padding: "0.5rem", fontFamily: "inherit" }}
            />
          </section>
          <section style={{ marginBottom: "1.5rem" }}>
            <label style={{ display: "block", fontWeight: 600, marginBottom: 0.25 }}>6.29(a)(ii) — Points raised by committee and response</label>
            <textarea
              value={sectionII}
              onChange={(e) => setSectionII(e.target.value)}
              rows={4}
              style={{ width: "100%", padding: "0.5rem", fontFamily: "inherit" }}
            />
          </section>
          <section style={{ marginBottom: "1.5rem" }}>
            <label style={{ display: "block", fontWeight: 600, marginBottom: 0.25 }}>6.29(a)(iii) — Recommendations / observations</label>
            <textarea
              value={sectionIII}
              onChange={(e) => setSectionIII(e.target.value)}
              rows={4}
              style={{ width: "100%", padding: "0.5rem", fontFamily: "inherit" }}
            />
          </section>
          <section style={{ marginBottom: "1.5rem" }}>
            <label style={{ display: "block", fontWeight: 600, marginBottom: 0.25 }}>Comments / change log</label>
            <textarea
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              rows={2}
              style={{ width: "100%", padding: "0.5rem", fontFamily: "inherit" }}
            />
          </section>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            <button
              type="button"
              onClick={handleSave}
              disabled={saving}
              style={{
                padding: "0.5rem 1rem",
                background: "#2563eb",
                color: "white",
                border: "none",
                borderRadius: 6,
                cursor: saving ? "wait" : "pointer",
              }}
            >
              {saving ? "Saving…" : "Save (new version)"}
            </button>
            <button
              type="button"
              onClick={handleFinalize}
              disabled={finalizing}
              style={{
                padding: "0.5rem 1rem",
                background: "#059669",
                color: "white",
                border: "none",
                borderRadius: 6,
                cursor: finalizing ? "wait" : "pointer",
              }}
            >
              {finalizing ? "Finalizing…" : "Finalize MoM"}
            </button>
          </div>
        </>
      )}
      <p style={{ marginTop: "2rem", fontSize: "0.875rem", color: "#64748b" }}>
        UGC policy: Mode A blocks &quot;Granted&quot; until UGC approval recorded; Mode B allows &quot;Subject to UGC&quot;.
      </p>
    </main>
  );
}
