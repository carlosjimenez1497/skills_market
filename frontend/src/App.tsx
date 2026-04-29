// import { useEffect, useMemo, useState } from "react";
import { useState } from "react";
import { useAuth } from "./hooks/useAuth";
import { useJobs } from "./hooks/useJobs";
import Auth from "./components/Auth";
import Home from "./components/Home";
import Browse from "./components/Browse";

type Track = "software" | "finance";

export default function App() {
  const auth = useAuth();
  const [page, setPage] = useState<"home" | "browse">("home");
  const [track, setTrack] = useState<Track | null>(null);

  const jobsHook = useJobs(track, page);

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
      <h1>Job Browser</h1>

      {page === "home" ? (
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
        />
      )}
    </div>
  );
}
