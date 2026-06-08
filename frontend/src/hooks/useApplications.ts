import { useCallback, useEffect, useState } from "react";
import { supabase } from "../supabase";

export type AppStatus = "saved" | "applied" | "interview" | "offer" | "rejected";

export type Application = {
  id: string;
  user_id: string;
  status: AppStatus;
  job_id: number | null;
  title: string | null;
  company: string | null;
  location: string | null;
  description: string | null;
  job_url: string | null;
  notes: string | null;
  applied_at: string | null;
  created_at: string;
  updated_at: string;
};

export type NewApplication = Omit<Application, "id" | "user_id" | "created_at" | "updated_at">;

export function useApplications() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setErr(null);
    try {
      const { data, error } = await supabase
        .from("user_applications")
        .select("*")
        .order("created_at", { ascending: false });
      if (error) throw error;
      setApplications((data as Application[]) ?? []);
    } catch (e: any) {
      setErr(e.message ?? "Failed to load applications");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function addApplication(app: NewApplication): Promise<Application> {
    const { data, error } = await supabase
      .from("user_applications")
      .insert([app])
      .select()
      .single();
    if (error) throw error;
    const inserted = data as Application;
    setApplications((prev) => [inserted, ...prev]);
    return inserted;
  }

  async function updateStatus(id: string, status: AppStatus) {
    const extra: Partial<Application> =
      status === "applied" ? { applied_at: new Date().toISOString() } : {};
    const { error } = await supabase
      .from("user_applications")
      .update({ status, ...extra, updated_at: new Date().toISOString() })
      .eq("id", id);
    if (error) throw error;
    setApplications((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status, ...extra } : a))
    );
  }

  async function updateNotes(id: string, notes: string) {
    const { error } = await supabase
      .from("user_applications")
      .update({ notes, updated_at: new Date().toISOString() })
      .eq("id", id);
    if (error) throw error;
    setApplications((prev) =>
      prev.map((a) => (a.id === id ? { ...a, notes } : a))
    );
  }

  async function removeApplication(id: string) {
    const { error } = await supabase
      .from("user_applications")
      .delete()
      .eq("id", id);
    if (error) throw error;
    setApplications((prev) => prev.filter((a) => a.id !== id));
  }

  return {
    applications,
    loading,
    err,
    addApplication,
    updateStatus,
    updateNotes,
    removeApplication,
    reload: load,
  };
}
