import { useEffect, useState } from "react";
import { fetchJobs, fetchJobsCount, type Job } from "../api";

type Track = "software" | "finance";

export function useJobs(track: Track | null, page: "home" | "browse") {
  const [language, setLanguage] = useState<string>("Any");
  const [keywordInput, setKeywordInput] = useState<string>("");

  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [pageNum, setPageNum] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [total, setTotal] = useState(0);

  const [searchTrigger, setSearchTrigger] = useState(0);

  const selectedJob = jobs.find((j) => j.id === selectedJobId) ?? null;
  const offset = (pageNum - 1) * pageSize;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  useEffect(() => {
    if (page !== "browse" || !track || searchTrigger === 0) return;

    setLoading(true);
    setErr(null);

    const langParam = language === "Any" ? undefined : language;
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
        setSelectedJobId(jobsData[0]?.id ?? null);
      })
      .catch((e) => setErr(e.message || "Unknown error"))
      .finally(() => setLoading(false));
  }, [page, track, pageSize, offset, searchTrigger]);

  useEffect(() => {
    if (page !== "browse" || !track) return;
    setPageNum(1);
  }, [page, track, language, keywordInput]);

  function resetJobs() {
    setLanguage("Any");
    setKeywordInput("");
    setJobs([]);
    setSelectedJobId(null);
    setPageNum(1);
    setTotal(0);
    setSearchTrigger(0);
  }

  return {
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
    resetJobs,
  };
}