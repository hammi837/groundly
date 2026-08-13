import { useState, type FormEvent } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../lib/auth";

export function LoginPage() {
  const { user, loading, login } = useAuth();
  const [email, setEmail] = useState("admin@riverside.demo");
  const [password, setPassword] = useState("riverside-demo");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (!loading && user) return <Navigate to="/" replace />;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(email.trim(), password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-screen">
      <div className="login-atmosphere" aria-hidden="true" />

      <section className="login-brand-pane">
        <div className="login-brand-inner">
          <img
            src="/brand/groundly-logo-lockup.png"
            alt="Groundly"
            className="login-brand-lockup"
          />
          <p className="login-brand-tagline">AI support that only answers from your docs</p>
          <ul className="login-brand-points">
            <li>Grounded answers with citations</li>
            <li>Graceful handoff when unsure</li>
            <li>Your content — never made up</li>
          </ul>
        </div>
        <div className="login-brand-orb login-brand-orb-a" aria-hidden="true" />
        <div className="login-brand-orb login-brand-orb-b" aria-hidden="true" />
      </section>

      <section className="login-form-pane">
        <form className="login-form" onSubmit={onSubmit}>
          <h1 className="login-form-title">Welcome back</h1>
          <p className="login-form-sub">Sign in to manage your grounded support agent.</p>

          <label className="login-field">
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="username"
              placeholder="you@company.com"
            />
          </label>

          <label className="login-field">
            <span>Password</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              placeholder="••••••••"
            />
          </label>

          {error ? <div className="login-error">{error}</div> : null}

          <button className="login-submit" type="submit" disabled={busy}>
            {busy ? "Signing in…" : "Sign in"}
          </button>

          <p className="login-footnote">Demo: admin@riverside.demo</p>
        </form>
      </section>
    </div>
  );
}
