interface AuthProps {
  authMode: "login" | "signup";
  setAuthMode: (mode: "login" | "signup") => void;
  email: string;
  setEmail: (email: string) => void;
  password: string;
  setPassword: (password: string) => void;
  authErr: string | null;
  authLoading: boolean;
  handleAuth: () => void;
}

export default function Auth({
  authMode,
  setAuthMode,
  email,
  setEmail,
  password,
  setPassword,
  authErr,
  authLoading,
  handleAuth,
}: AuthProps) {
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
            setAuthMode(authMode === "login" ? "signup" : "login");
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