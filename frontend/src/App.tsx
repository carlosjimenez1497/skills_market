// import { useEffect, useMemo, useState } from "react";
import { useEffect, useState } from "react";
import { fetchJobs, fetchJobsCount, type Job } from "./api";
import { supabase } from "./supabase";


type Track = "software" | "finance";

// function toKeywordsCsv(raw: string) {
//   return raw
//     .split(/[,;]+|\s{2,}|\n|\t| /g)
//     .map((s) => s.trim())
//     .filter(Boolean)
//     .join(",");
// }

export default function App() {
  // ========================
  // AUTH STATE
  // ========================
  const [session, setSession] = useState<any>(null);
  const [authMode, setAuthMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authErr, setAuthErr] = useState<string | null>(null);
  const [authLoading, setAuthLoading] = useState(false);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
    });

    const { data: sub } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session);
      }
    );

    return () => sub.subscription.unsubscribe();
  }, []);

  async function handleAuth() {
    setAuthLoading(true);
    setAuthErr(null);

    try {
      if (authMode === "signup") {
        const { error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        setAuthErr("Check your email to confirm your account.");
      } else {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
      }
    } catch (e: any) {
      setAuthErr(e.message ?? "Auth error");
    } finally {
      setAuthLoading(false);
    }
  }

  async function handleLogout() {
    await supabase.auth.signOut();
  }

  // ========================
  // APP STATE (LOGGED IN)
  // ========================
  const [page, setPage] = useState<"home" | "browse">("home");
  const [track, setTrack] = useState<Track | null>(null);

  const [language, setLanguage] = useState<string>("Any");
  const [keywordInput, setKeywordInput] = useState<string>("");

  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [pageNum, setPageNum] = useState(1);
  const [pageSize, setPageSize] = useState(25); // choose 25/50
  const [total, setTotal] = useState(0);

  const selectedJob = jobs.find((j) => j.id === selectedJobId) ?? null;
  const offset = (pageNum - 1) * pageSize;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  useEffect(() => {
    if (page !== "browse" || !track) return;

    setLoading(true);
    setErr(null);

    const langParam = language === "Any" ? undefined : language;
    // const kwCsv = keywordsCsv || undefined;
    const kw = keywordInput.trim() || undefined;

    Promise.all([
      fetchJobs({
        track,
        language: langParam,
        keywords: kw,
        limit: pageSize,
        offset,
      }),
      fetchJobsCount({
        track,
        language: langParam,
        keywords: kw,
      }),
    ])
      .then(([jobsData, countData]) => {
        setJobs(jobsData);
        setTotal(countData.total);

        // keep selection meaningful on new pages/results
        setSelectedJobId(jobsData[0]?.id ?? null);
      })
      .catch((e) => setErr(e.message || "Unknown error"))
      .finally(() => setLoading(false));
  }, [page, track, language, keywordInput, pageSize, offset]);


  useEffect(() => {
    if (page !== "browse" || !track) return;
    setPageNum(1);
  }, [page, track, language, keywordInput]);

  // ========================
  // IF NOT LOGGED IN → SHOW AUTH
  // ========================
  if (!session) {
    return (
      <div style={{ padding: 40, maxWidth: 420, margin: "0 auto" }}>
        <h1>{authMode === "login" ? "Log in" : "Sign up"}</h1>

        <div style={{ display: "grid", gap: 10 }}>
          <input
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button
            onClick={handleAuth}
            disabled={!email || !password || authLoading}
          >
            {authLoading
              ? "..."
              : authMode === "login"
              ? "Log in"
              : "Create account"}
          </button>

          {authErr && (
            <div style={{ color: authErr.includes("Check") ? "black" : "crimson" }}>
              {authErr}
            </div>
          )}

          <button
            onClick={() => {
              setAuthErr(null);
              setAuthMode((m) => (m === "login" ? "signup" : "login"));
            }}
          >
            {authMode === "login"
              ? "Need an account? Sign up"
              : "Have an account? Log in"}
          </button>
        </div>
      </div>
    );
  }

  

  // ========================
  // MAIN APP UI
  // ========================
  return (
    <div style={{ fontFamily: "system-ui", padding: 20, maxWidth: 1400, margin: "0 auto" }}>
      <h1>Job Browser</h1>

      {page === "home" ? (
        <div style={{ display: "grid", gap: 12, gridTemplateColumns: "1fr 1fr", marginTop: 16 }}>
          <button
            style={{ padding: 18, borderRadius: 12, border: "1px solid #ddd", textAlign: "left" }}
            onClick={() => {
              setTrack("software");
              setPage("browse");
            }}
          >
            <div style={{ fontSize: 18, fontWeight: 700 }}>Software</div>
            <div style={{ opacity: 0.7 }}>Backend, C++, SDET, data…</div>
          </button>

          <button
            style={{ padding: 18, borderRadius: 12, border: "1px solid #ddd", textAlign: "left" }}
            onClick={() => {
              setTrack("finance");
              setPage("browse");
            }}
          >
            <div style={{ fontSize: 18, fontWeight: 700 }}>Finance</div>
            <div style={{ opacity: 0.7 }}>Quant, analyst, modeling…</div>
          </button>
        </div>
      ) : (
        <>
          <div style={{ marginTop: 16, display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
            <button
              onClick={() => {
                setPage("home");
                setTrack(null);
                setLanguage("Any");
                setKeywordInput("");
                setJobs([]);
                setSelectedJobId(null); // ✅ reset selection when leavingZ
              }}
            >
              ← Back
            </button>

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
                    onClick={() => setPageNum((p) => Math.max(1, p - 1))}
                    disabled={pageNum <= 1}
                  >
                    ← Prev
                  </button>
                  <button
                    onClick={() => setPageNum((p) => Math.min(totalPages, p + 1))}
                    disabled={pageNum >= totalPages}
                  >
                    Next →
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* ✅ NEW: 2-column layout */}
          <div
            style={{
              display: "flex",
              height: "100vh", // 🔑 constrain height
              gap: 12,
              padding: 12,
            }}
          >
            {/* LEFT: job list */}
            <div
              style={{
                flex: 1,
                overflowY: "auto", // 🔑 own scroll
                border: "1px solid #ddd",
                borderRadius: 8,
                padding: 8,
              }}
            >
              {jobs.map((j) => {
                const isSelected = j.id === selectedJobId;

                return (
                  <button
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
                      {/* Keep link for opening, but selection is by clicking the card */}
                      <a
                        href={j.source_url}
                        target="_blank"
                        rel="noreferrer"
                        onClick={(e) => e.stopPropagation()} // ✅ prevents selecting when clicking link
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

                    <div style={{ marginTop: 8, fontSize: 12, opacity: 0.7 }}>
                      Source: {j.source}
                    </div>
                  </button>
                );
              })}
            </div>

            {/* RIGHT: selected job details */}
            <div
              style={{
                flex: 1,
                overflowY: "auto", // 🔑 own scroll
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
      )}
    </div>
);

}
