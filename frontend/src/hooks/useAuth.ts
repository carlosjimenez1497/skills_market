import { useEffect, useState } from "react";
import { supabase } from "../supabase";

export function useAuth() {
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

  return {
    session,
    authMode,
    setAuthMode,
    email,
    setEmail,
    password,
    setPassword,
    authErr,
    authLoading,
    handleAuth,
    handleLogout,
  };
}