import { useState } from "react";
import { useAuth } from "./hooks/useAuth";
import { useJobs } from "./hooks/useJobs";
import { supabase } from "./supabase";
import { type Job } from "./api";
import Auth from "./components/Auth";
import Home from "./components/Home";
import Browse from "./components/Browse";
import Board from "./components/Board";

type Track = "software" | "finance";
type Page = "home" | "browse" | "board";

export default function App() {
  const auth = useAuth();
  const [page, setPage] = useState<Page>("home");
  const [track, setTrack] = useState<Track | null>(null);

  const jobsHook = useJobs(track, page === "browse" ? "browse" : "home");

  const handleSelectTrack = (selectedTrack: Track) => {
    setTrack(selectedTrack);
    setPage("browse");
    jobsHook.setSearchTrigger(1);
  };

  const handleBack = () => {
    setPage("home");
    setTrack(null);
    jobsHook.resetJobs();
  };

  async function handleSaveToBoard(job: Job) {
    const { data: { user } } = await supabase.auth.getUser();
    const { error } = await supabase.from("user_applications").insert([{
      user_id: user?.id,
      status: "saved",
      job_id: job.id,
      title: job.title,
      company: job.company,
      location: job.location,
      description: job.description,
      job_url: job.job_view_url ?? job.source_url,
    }]);
    if (error) throw new Error(error.message);
  }

  if (!auth.session) {
    return (
      <Auth
        authMode={auth.authMode}
        setAuthMode={auth.setAuthMode}
        email={auth.email}
        setEmail={auth.setEmail}
        password={auth.password}
        setPassword={auth.setPassword}
        authErr={auth.authErr}
        authLoading={auth.authLoading}
        handleAuth={auth.handleAuth}
      />
    );
  }

  return (
    <div style={{ fontFamily: "system-ui", padding: 20, maxWidth: 1400, margin: "0 auto" }}>
      {/* Top nav */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <h1
          style={{ margin: 0, cursor: "pointer", fontSize: 22 }}
          onClick={() => { setPage("home"); setTrack(null); jobsHook.resetJobs(); }}
        >
          Job Browser
        </h1>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <button
            onClick={() => setPage("board")}
            style={{
              borderRadius: 6,
              padding: "6px 14px",
              fontWeight: page === "board" ? 700 : 400,
              background: page === "board" ? "#eff6ff" : "white",
              border: `1px solid ${page === "board" ? "#bfdbfe" : "#d1d5db"}`,
              color: page === "board" ? "#1d4ed8" : "inherit",
              cursor: "pointer",
              fontSize: 13,
            }}
          >
            My Board
          </button>
          <button
            onClick={auth.handleLogout}
            style={{ fontSize: 12, opacity: 0.5, background: "none", border: "none", cursor: "pointer" }}
          >
            Sign out
          </button>
        </div>
      </div>

      {/* Page content */}
      {page === "board" ? (
        <Board />
      ) : page === "home" ? (
        <Home onSelectTrack={handleSelectTrack} />
      ) : (
        <Browse
          track={track!}
          onBack={handleBack}
          language={jobsHook.language}
          setLanguage={jobsHook.setLanguage}
          keywordInput={jobsHook.keywordInput}
          setKeywordInput={jobsHook.setKeywordInput}
          jobs={jobsHook.jobs}
          loading={jobsHook.loading}
          err={jobsHook.err}
          selectedJobId={jobsHook.selectedJobId}
          setSelectedJobId={jobsHook.setSelectedJobId}
          pageNum={jobsHook.pageNum}
          setPageNum={jobsHook.setPageNum}
          pageSize={jobsHook.pageSize}
          setPageSize={jobsHook.setPageSize}
          total={jobsHook.total}
          searchTrigger={jobsHook.searchTrigger}
          setSearchTrigger={jobsHook.setSearchTrigger}
          selectedJob={jobsHook.selectedJob}
          offset={jobsHook.offset}
          totalPages={jobsHook.totalPages}
          onSaveToBoard={handleSaveToBoard}
        />
      )}
    </div>
  );
}
