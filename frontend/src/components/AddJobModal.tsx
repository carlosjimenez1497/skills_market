import { useState } from "react";
import type { AppStatus, NewApplication } from "../hooks/useApplications";

const API = import.meta.env.VITE_API_BASE;

const METHOD_LABEL: Record<string, string> = {
  jsonld: "structured data (JSON-LD)",
  opengraph: "OpenGraph meta tags",
  heuristic: "page heuristics",
  llm: "AI extraction",
  partial: "partial extraction",
};

interface Props {
  onClose: () => void;
  onSave: (data: NewApplication) => Promise<void>;
}

export default function AddJobModal({ onClose, onSave }: Props) {
  const [url, setUrl] = useState("");
  const [fetching, setFetching] = useState(false);
  const [fetchMethod, setFetchMethod] = useState<string | null>(null);
  const [fetchErr, setFetchErr] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveErr, setSaveErr] = useState<string | null>(null);

  const [form, setForm] = useState<Partial<NewApplication>>({
    status: "saved",
    job_id: null,
    title: null,
    company: null,
    location: null,
    description: null,
    job_url: null,
    notes: null,
    applied_at: null,
  });

  async function handleFetch() {
    const trimmed = url.trim();
    if (!trimmed) return;
    setFetching(true);
    setFetchErr(null);
    setFetchMethod(null);
    try {
      const res = await fetch(`${API}/api/jobs/fetch-url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: trimmed }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail ?? `Server error ${res.status}`);
      }
      const data = await res.json();
      setForm((prev) => ({
        ...prev,
        title: data.title ?? prev.title,
        company: data.company ?? prev.company,
        location: data.location ?? prev.location,
        description: data.description ?? prev.description,
        job_url: data.job_url ?? trimmed,
      }));
      setFetchMethod(data.method ?? null);
    } catch (e: any) {
      setFetchErr(e.message ?? "Fetch failed — fill in fields manually below.");
      setForm((prev) => ({ ...prev, job_url: prev.job_url ?? trimmed }));
    } finally {
      setFetching(false);
    }
  }

  async function handleSave() {
    setSaveErr(null);
    setSaving(true);
    try {
      await onSave({
        ...form,
        status: (form.status as AppStatus) ?? "saved",
        job_id: form.job_id ?? null,
        job_url: form.job_url ?? (url.trim() || null),
        title: form.title ?? null,
        company: form.company ?? null,
        location: form.location ?? null,
        description: form.description ?? null,
        notes: form.notes ?? null,
        applied_at: null,
      });
    } catch (e: any) {
      setSaveErr(e.message ?? "Save failed");
    } finally {
      setSaving(false);
    }
  }

  function setField(key: keyof NewApplication) {
    return (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm((prev) => ({ ...prev, [key]: e.target.value || null }));
  }

  const canSave = !saving && (!!form.title || !!form.job_url || !!url.trim());

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.45)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        style={{
          background: "white",
          borderRadius: 12,
          padding: 24,
          width: "min(540px, 95vw)",
          maxHeight: "90vh",
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
          gap: 14,
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3 style={{ margin: 0 }}>Add Job</h3>
          <button
            onClick={onClose}
            style={{ background: "none", border: "none", fontSize: 20, cursor: "pointer", lineHeight: 1 }}
          >
            ×
          </button>
        </div>

        {/* URL fetch row */}
        <div style={{ display: "flex", gap: 8 }}>
          <input
            type="url"
            placeholder="Paste job URL to auto-fill…"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleFetch()}
            style={{ flex: 1, borderRadius: 6, border: "1px solid #d1d5db", padding: "6px 10px", fontSize: 13 }}
          />
          <button
            onClick={handleFetch}
            disabled={fetching || !url.trim()}
            style={{ borderRadius: 6, padding: "6px 14px", cursor: "pointer" }}
          >
            {fetching ? "Fetching…" : "Fetch"}
          </button>
        </div>

        {fetchErr && (
          <div style={{ color: "#b45309", fontSize: 12, background: "#fef3c7", borderRadius: 6, padding: "6px 10px" }}>
            {fetchErr}
          </div>
        )}
        {fetchMethod && !fetchErr && (
          <div style={{ fontSize: 11, opacity: 0.55 }}>
            Extracted via {METHOD_LABEL[fetchMethod] ?? fetchMethod}
          </div>
        )}

        {/* Form fields */}
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {(
            [
              { label: "Title", key: "title" },
              { label: "Company", key: "company" },
              { label: "Location", key: "location" },
              { label: "Job URL", key: "job_url" },
            ] as const
          ).map(({ label, key }) => (
            <label key={key} style={{ display: "flex", flexDirection: "column", gap: 3 }}>
              <span style={{ fontSize: 12, fontWeight: 600, color: "#374151" }}>{label}</span>
              <input
                type="text"
                value={(form[key] as string) ?? ""}
                onChange={setField(key)}
                style={{ borderRadius: 6, border: "1px solid #d1d5db", padding: "6px 10px", fontSize: 13 }}
              />
            </label>
          ))}

          <label style={{ display: "flex", flexDirection: "column", gap: 3 }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: "#374151" }}>Description</span>
            <textarea
              rows={5}
              value={(form.description as string) ?? ""}
              onChange={setField("description")}
              style={{ borderRadius: 6, border: "1px solid #d1d5db", padding: "6px 10px", fontSize: 13, resize: "vertical" }}
            />
          </label>

          <label style={{ display: "flex", flexDirection: "column", gap: 3 }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: "#374151" }}>Notes</span>
            <textarea
              rows={3}
              value={(form.notes as string) ?? ""}
              onChange={setField("notes")}
              placeholder="Personal notes…"
              style={{ borderRadius: 6, border: "1px solid #d1d5db", padding: "6px 10px", fontSize: 13, resize: "vertical" }}
            />
          </label>
        </div>

        {saveErr && (
          <div style={{ color: "crimson", fontSize: 12 }}>Save failed: {saveErr}</div>
        )}

        {/* Actions */}
        <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
          <button onClick={onClose} style={{ borderRadius: 6, padding: "7px 16px", cursor: "pointer" }}>
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={!canSave}
            style={{
              borderRadius: 6,
              padding: "7px 16px",
              cursor: canSave ? "pointer" : "not-allowed",
              background: canSave ? "#2563eb" : "#93c5fd",
              color: "white",
              border: "none",
              fontWeight: 600,
            }}
          >
            {saving ? "Saving…" : "Save to board"}
          </button>
        </div>
      </div>
    </div>
  );
}
