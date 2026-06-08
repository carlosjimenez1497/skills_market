import { useState, useEffect } from "react";
import { type Job } from "../api";
import { supabase } from "../supabase";

type Track = "software" | "finance";

interface BrowseProps {
  track: Track;
  onBack: () => void;
  language: string;
  setLanguage: (lang: string) => void;
  keywordInput: string;
  setKeywordInput: (kw: string) => void;
  jobs: Job[];
  loading: boolean;
  err: string | null;
  selectedJobId: number | null;
  setSelectedJobId: (id: number | null) => void;
  pageNum: number;
  setPageNum: (page: number) => void;
  pageSize: number;
  setPageSize: (size: number) => void;
  total: number;
  searchTrigger: number;
  setSearchTrigger: (trigger: number) => void;
  selectedJob: Job | null;
  offset: number;
  totalPages: number;
  onSaveToBoard: (job: Job) => Promise<void>;
}

export default function Browse({
  track,
  onBack,
  language,
  setLanguage,
  keywordInput,
  setKeywordInput,
  jobs,
  loading,
  err,
  selectedJobId,
  setSelectedJobId,
  pageNum,
  setPageNum,
  pageSize,
  setPageSize,
  total,
  searchTrigger,
  setSearchTrigger,
  selectedJob,
  offset,
  totalPages,
  onSaveToBoard,
}: BrowseProps) {
  const [savedIds, setSavedIds] = useState<Set<number>>(new Set());

  useEffect(() => {
    if (jobs.length === 0) return;
    const jobIds = jobs.map((j) => j.id);
    supabase
      .from("user_applications")
      .select("job_id")
      .in("job_id", jobIds)
      .then(({ data }) => {
        if (data) setSavedIds(new Set(data.map((row) => row.job_id)));
      });
  }, [jobs]);

  async function handleSave(job: Job) {
    await onSaveToBoard(job);
    setSavedIds((prev) => new Set(prev).add(job.id));
  }
  return (
    <>
      <div style={{ marginTop: 16, display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
        <button onClick={onBack}>← Back</button>

        <div><b>Track:</b> {track}</div>

        <label style={{ display: "flex", gap: 6, alignItems: "center" }}>
          Language:
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option>Any</option>
            <option>en</option>
            <option>it</option>
            <option>sp</option>
            <option>nl</option>
          </select>
        </label>

        <label style={{ display: "flex", gap: 6, alignItems: "center", flex: 1, minWidth: 280 }}>
          Keywords:
          <input
            style={{ flex: 1 }}
            placeholder='e.g. "fastapi docker" or "statistics backtesting"'
            value={keywordInput}
            onChange={(e) => setKeywordInput(e.target.value)}
          />
        </label>

        <button onClick={() => { setLanguage("Any"); setKeywordInput(""); }}>
          Clear
        </button>

        <button onClick={() => setSearchTrigger(searchTrigger + 1)}>
          Search
        </button>
      </div>

      <div style={{ marginTop: 12 }}>
        {loading && <div>Loading…</div>}
        {err && <div style={{ color: "crimson" }}>Error: {err}</div>}
        {!loading && !err && (
          <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap", opacity: 0.85 }}>
            <div>
              Results:{" "}
              {total === 0
                ? "0"
                : `${offset + 1}–${Math.min(offset + jobs.length, total)} of ${total}`}
              {" "}
              (page {pageNum}/{totalPages})
            </div>

            <label style={{ display: "flex", gap: 6, alignItems: "center" }}>
              Page size:
              <select value={pageSize} onChange={(e) => setPageSize(Number(e.target.value))}>
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
              </select>
            </label>

            <div style={{ display: "flex", gap: 8 }}>
              <button
                onClick={() => setPageNum(Math.max(1, pageNum - 1))}
                disabled={pageNum <= 1}
              >
                ← Prev
              </button>
              <button
                onClick={() => setPageNum(Math.min(totalPages, pageNum + 1))}
                disabled={pageNum >= totalPages}
              >
                Next →
              </button>
            </div>
          </div>
        )}
      </div>

      <div
        style={{
          display: "flex",
          height: "100vh",
          gap: 12,
          padding: 12,
        }}
      >
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            border: "1px solid #ddd",
            borderRadius: 8,
            padding: 8,
          }}
        >
          {jobs.map((j) => {
            const isSelected = j.id === selectedJobId;

            return (
              <div
                key={j.id}
                onClick={() => setSelectedJobId(j.id)}
                style={{
                  border: "1px solid #ddd",
                  borderRadius: 12,
                  padding: 12,
                  textAlign: "left",
                  cursor: "pointer",
                  background: isSelected ? "#f5f5f5" : "white",
                }}
              >
                <div style={{ fontWeight: 700 }}>
                  <a
                    href={j.source_url}
                    target="_blank"
                    rel="noreferrer"
                    onClick={(e) => e.stopPropagation()}
                  >
                    {j.title ?? "(no title)"}
                  </a>
                </div>

                <div style={{ opacity: 0.8 }}>
                  {(j.company ?? "Unknown company")}{j.location ? ` • ${j.location}` : ""}
                </div>

                {j.description && (
                  <div style={{ marginTop: 8, opacity: 0.85 }}>
                    {j.description.slice(0, 160)}{j.description.length > 160 ? "…" : ""}
                  </div>
                )}

                <div style={{ marginTop: 8, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <span style={{ fontSize: 12, opacity: 0.7 }}>Source: {j.source}</span>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleSave(j); }}
                    disabled={savedIds.has(j.id)}
                    style={{
                      fontSize: 11,
                      borderRadius: 4,
                      padding: "2px 8px",
                      cursor: savedIds.has(j.id) ? "default" : "pointer",
                      background: savedIds.has(j.id) ? "#d1fae5" : "#eff6ff",
                      border: `1px solid ${savedIds.has(j.id) ? "#6ee7b7" : "#bfdbfe"}`,
                      color: savedIds.has(j.id) ? "#065f46" : "#1d4ed8",
                    }}
                  >
                    {savedIds.has(j.id) ? "✓ Saved" : "+ Save"}
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        <div
          style={{
            flex: 1,
            overflowY: "auto",
            border: "1px solid #ddd",
            borderRadius: 8,
            padding: 8,
          }}
        >
          {!selectedJob ? (
            <div style={{ opacity: 0.7 }}>Click a job to see details.</div>
          ) : (
            <>
              <div style={{ fontSize: 18, fontWeight: 800 }}>
                {selectedJob.job_view_url ? (
                  <a
                    href={selectedJob.job_view_url}
                    target="_blank"
                    rel="noreferrer"
                    style={{
                      color: "inherit",
                      textDecoration: "underline",
                      cursor: "pointer",
                    }}
                  >
                    {selectedJob.title ?? "(no title)"}
                  </a>
                ) : (
                  selectedJob.title ?? "(no title)"
                )}
              </div>

              <div style={{ marginTop: 6, opacity: 0.85 }}>
                <b>{selectedJob.company ?? "Unknown company"}</b>
                {selectedJob.location ? ` • ${selectedJob.location}` : ""}
              </div>

              <div style={{ marginTop: 8, fontSize: 12, opacity: 0.7 }}>
                Source: {selectedJob.source}
              </div>

              {selectedJob.source_url && (
                <div style={{ marginTop: 10 }}>
                  <a href={selectedJob.source_url} target="_blank" rel="noreferrer">
                    Open posting
                  </a>
                </div>
              )}

              <div style={{ marginTop: 12, whiteSpace: "pre-wrap", lineHeight: 1.45 }}>
                {selectedJob.description ?? "(no description)"}
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}