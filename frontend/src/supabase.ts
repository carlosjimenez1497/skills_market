import { createClient } from "@supabase/supabase-js";

const url = import.meta.env.VITE_SUPABASE_URL;
const anon = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!url) throw new Error("VITE_SUPABASE_URL is not set");
if (!anon) throw new Error("VITE_SUPABASE_ANON_KEY is not set");

export const supabase = createClient(url, anon);