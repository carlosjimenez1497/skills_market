import { useState } from "react";
import {
  useApplications,
  type Application,
  type AppStatus,
  type NewApplication,
} from "../hooks/useApplications";
import AddJobModal from "./AddJobModal";

const STATUSES: AppStatus[] = ["saved", "applied", "interview", "offer", "rejected"];

const STATUS_LABEL: Record<AppStatus, string> = {
  saved: "Saved",
  applied: "Applied",
  interview: "Interview",
  offer: "Offer",
  rejected: "Rejected",
};

const STATUS_COLOR: Record<AppStatus, string> = {
  saved: "#6b7280",
  applied: "#2563eb",
  interview: "#d97706",
  offer: "#16a34a",
  rejected: "#dc2626",
};

interface CardProps {
  app: Application;
  onStatusChange: (id: string, status: AppStatus) => void;
  onSaveNotes: (id: string, notes: string) => void;
  onRemove: (id: string) => void;
}

function AppCard({ app, onStatusChange, onSaveNotes, onRemove }: CardProps) {
  const [expanded, setExpanded] = useState(false);
  const [notes, setNotes] = useState(app.notes ?? "");

  return (
    <div
      style={{
        background: "white",
        border: "1px solid #e5e7eb",
        borderRadius: 8,
        padding: 10,
        fontSize: 13,
      }}
    >
      {/* Title row */}
      <div
        style={{ fontWeight: 600, cursor: "pointer", lineHeight: 1.3 }}
        onClick={() => setExpanded((v) => !v)}
        title={expanded ? "Collapse" : "Expand"}
      >
        {app.title ?? "(no title)"}
        <span style={{ fontSize: 11, marginLeft: 6, opacity: 0.4 }}>{expanded ? "▲" : "▼"}</span>
      </div>

      {/* Company / location */}
      <div style={{ fontSize: 12, opacity: 0.6, marginTop: 2 }}>
        {[app.company, app.location].filter(Boolean).join(" • ") || <>&nbsp;</>}
      </div>

      {/* Expanded detail */}
      {expanded && (
        <div style={{ marginTop: 8, display: "flex", flexDirection: "column", gap: 8 }}>
          {app.description && (
            <div
              style={{
                fontSize: 12,
                opacity: 0.8,
                maxHeight: 140,
                overflowY: "auto",
                whiteSpace: "pre-wrap",
                lineHeight: 1.4,
                background: "#f9fafb",
                borderRadius: 4,
                padding: "6px 8px",
              }}
            >
              {app.description.slice(0, 500)}
              {app.description.length > 500 ? "…" : ""}
            </div>
          )}

          <textarea
            rows={3}
            placeholder="Notes…"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            style={{
              fontSize: 12,
              borderRadius: 4,
              border: "1px solid #d1d5db",
              padding: "4px 6px",
              resize: "vertical",
              width: "100%",
              boxSizing: "border-box",
            }}
          />
          <button
            style={{ fontSize: 11, alignSelf: "flex-start", borderRadius: 4, padding: "3px 8px", cursor: "pointer" }}
            onClick={() => onSaveNotes(app.id, notes)}
          >
            Save notes
          </button>
        </div>
      )}

      {/* Action row */}
      <div style={{ display: "flex", gap: 6, marginTop: 8, alignItems: "center" }}>
        {app.job_url && (
          <a
            href={app.job_url}
            target="_blank"
            rel="noreferrer"
            style={{ fontSize: 11, flexShrink: 0 }}
          >
            ↗ Open
          </a>
        )}

        <select
          value={app.status}
          onChange={(e) => onStatusChange(app.id, e.target.value as AppStatus)}
          style={{ fontSize: 11, flex: 1, borderRadius: 4, border: "1px solid #d1d5db", padding: "2px 4px" }}
        >
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {STATUS_LABEL[s]}
            </option>
          ))}
        </select>

        <button
          title="Remove"
          onClick={() => {
            if (window.confirm(`Remove "${app.title ?? "this job"}"?`)) onRemove(app.id);
          }}
          style={{
            background: "none",
            border: "none",
            color: "#ef4444",
            cursor: "pointer",
            fontSize: 14,
            lineHeight: 1,
            padding: "0 2px",
            flexShrink: 0,
          }}
        >
          ×
        </button>
      </div>
    </div>
  );
}

export default function Board() {
  const { applications, loading, err, addApplication, updateStatus, updateNotes, removeApplication } =
    useApplications();
  const [showAddModal, setShowAddModal] = useState(false);

  if (loading) return <div style={{ padding: 20 }}>Loading board…</div>;
  if (err) return <div style={{ padding: 20, color: "crimson" }}>Error: {err}</div>;

  const byStatus = (s: AppStatus) => applications.filter((a) => a.status === s);

  async function handleSave(data: NewApplication) {
    await addApplication(data);
    setShowAddModal(false);
  }

  return (
    <div>
      {/* Board header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 16,
        }}
      >
        <div style={{ opacity: 0.6, fontSize: 13 }}>
          {applications.length} job{applications.length !== 1 ? "s" : ""} tracked
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          style={{
            borderRadius: 6,
            padding: "7px 14px",
            background: "#2563eb",
            color: "white",
            border: "none",
            cursor: "pointer",
            fontWeight: 600,
            fontSize: 13,
          }}
        >
          + Import job
        </button>
      </div>

      {/* Kanban columns */}
      <div style={{ display: "flex", gap: 10, overflowX: "auto", alignItems: "flex-start", paddingBottom: 16 }}>
        {STATUSES.map((status) => {
          const cards = byStatus(status);
          return (
            <div key={status} style={{ flex: "0 0 220px", minWidth: 220 }}>
              {/* Column header */}
              <div
                style={{
                  background: STATUS_COLOR[status],
                  color: "white",
                  borderRadius: "8px 8px 0 0",
                  padding: "8px 12px",
                  fontWeight: 700,
                  fontSize: 13,
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <span>{STATUS_LABEL[status]}</span>
                <span
                  style={{
                    background: "rgba(255,255,255,0.25)",
                    borderRadius: 10,
                    padding: "1px 7px",
                    fontSize: 11,
                  }}
                >
                  {cards.length}
                </span>
              </div>

              {/* Cards */}
              <div
                style={{
                  border: "1px solid #e5e7eb",
                  borderTop: "none",
                  borderRadius: "0 0 8px 8px",
                  padding: 8,
                  minHeight: 100,
                  background: "#f9fafb",
                  display: "flex",
                  flexDirection: "column",
                  gap: 8,
                }}
              >
                {cards.length === 0 && (
                  <div style={{ fontSize: 12, opacity: 0.35, textAlign: "center", paddingTop: 12 }}>
                    Empty
                  </div>
                )}
                {cards.map((app) => (
                  <AppCard
                    key={app.id}
                    app={app}
                    onStatusChange={updateStatus}
                    onSaveNotes={updateNotes}
                    onRemove={removeApplication}
                  />
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {showAddModal && (
        <AddJobModal onClose={() => setShowAddModal(false)} onSave={handleSave} />
      )}
    </div>
  );
}
