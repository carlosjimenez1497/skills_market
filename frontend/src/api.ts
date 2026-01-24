const API = import.meta.env.VITE_API_BASE;
if (!API) throw new Error("VITE_API_BASE is not set");
export type Job = {
  id: number;
  source: string;
  source_url: string;
  company?: string | null;
  title?: string | null;
  location?: string | null;
  description?: string | null;
  job_view_url?: string | null;
};

export type JobsCount = { total: number };

export async function fetchJobs(params: {
  track?: string;
  language?: string;
  keywords?: string; // comma-separated
  limit?: number;
  offset?: number;
}): Promise<Job[]> {
  const url = new URL(`${API}/api/jobs`);
  Object.entries(params).forEach(([k, v]) => {
    if (v === undefined || v === null || v === "") return;
    url.searchParams.set(k, String(v));
  });

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}


export async function fetchJobsCount(params: {
  track?: string;
  language?: string;
  keywords?: string;
}): Promise<JobsCount> {
  const url = new URL(`${API}/api/jobs/count`);
  Object.entries(params).forEach(([k, v]) => {
    if (v === undefined || v === null || v === "") return;
    url.searchParams.set(k, String(v));
  });

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}