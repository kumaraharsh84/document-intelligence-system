import { useContext, useState } from "react";
import { Navigate } from "react-router-dom";

import { AuthContext } from "../context/AuthContext";

export default function Login() {
  // Render the login and registration page for the application.
  const { user, login } = useContext(AuthContext);
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (event) => {
    // Submit either a login or registration request to the backend.
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(form.email, form.password, mode);
    } catch (submitError) {
      setError(submitError.response?.data?.error || "Unable to authenticate.");
    } finally {
      setBusy(false);
    }
  };

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_#fff9f0,_#f6efe4_50%,_#d7e3ef)] px-6">
      <div className="w-full max-w-md rounded-[2rem] bg-white p-8 shadow-xl shadow-ink/10">
        <p className="text-sm uppercase tracking-[0.3em] text-ember">Document Intelligence</p>
        <h1 className="mt-4 font-display text-4xl text-ink">{mode === "login" ? "Welcome back" : "Create account"}</h1>
        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          <input
            type="email"
            placeholder="Email address"
            value={form.email}
            onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
            className="w-full rounded-2xl border border-ink/10 px-4 py-3 outline-none focus:border-moss"
          />
          <input
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
            className="w-full rounded-2xl border border-ink/10 px-4 py-3 outline-none focus:border-moss"
          />
          {error ? <p className="text-sm text-rose-600">{error}</p> : null}
          <button type="submit" disabled={busy} className="w-full rounded-2xl bg-ink px-4 py-3 font-medium text-white">
            {busy ? "Please wait..." : mode === "login" ? "Login" : "Register"}
          </button>
        </form>
        <button
          type="button"
          onClick={() => setMode((current) => (current === "login" ? "register" : "login"))}
          className="mt-4 text-sm text-moss"
        >
          {mode === "login" ? "Need an account? Register" : "Already have an account? Login"}
        </button>
      </div>
    </div>
  );
}
