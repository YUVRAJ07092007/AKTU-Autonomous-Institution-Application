import { useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export default function Home() {
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/health`, {
        headers: {
          "x-user-id": "frontend",
          "x-roles": "FRONTEND_VIEWER"
        }
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (e: any) {
      setError(e.message ?? "Health check failed");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main
      style={{
        minHeight: "100vh",
        fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#f5f5f7"
      }}
    >
      <div
        style={{
          background: "white",
          padding: "2rem 2.5rem",
          borderRadius: "1rem",
          boxShadow: "0 18px 45px rgba(15, 23, 42, 0.12)",
          maxWidth: "640px",
          width: "100%"
        }}
      >
        <h1 style={{ fontSize: "1.875rem", marginBottom: "0.5rem" }}>
          AKTU Academic Autonomy Portal
        </h1>
        <p style={{ color: "#4b5563", marginBottom: "1.5rem" }}>
          API base URL: <code>{API_BASE_URL}</code>
        </p>
        <button
          onClick={checkHealth}
          disabled={loading}
          style={{
            background:
              "linear-gradient(135deg, #2563eb 0%, #4f46e5 50%, #7c3aed 100%)",
            color: "white",
            border: "none",
            borderRadius: "999px",
            padding: "0.75rem 1.5rem",
            fontWeight: 600,
            cursor: loading ? "wait" : "pointer",
            boxShadow: "0 10px 25px rgba(37, 99, 235, 0.35)",
            marginBottom: "1rem"
          }}
        >
          {loading ? "Checking..." : "Run /api/health"}
        </button>
        {error && (
          <p style={{ color: "#b91c1c", marginBottom: "0.75rem" }}>{error}</p>
        )}
        {result && (
          <pre
            style={{
              background: "#0f172a",
              color: "#e5e7eb",
              padding: "1rem",
              borderRadius: "0.75rem",
              fontSize: "0.875rem",
              overflowX: "auto"
            }}
          >
            {result}
          </pre>
        )}
      </div>
    </main>
  );
}

