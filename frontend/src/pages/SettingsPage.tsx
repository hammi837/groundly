import { useEffect, useState, type FormEvent } from "react";
import { api } from "../lib/api";
import type { Settings } from "../types";

export function SettingsPage() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState("");
  const [busy, setBusy] = useState(false);
  const [startersText, setStartersText] = useState("");
  const [originsText, setOriginsText] = useState("");
  const [revealedKey, setRevealedKey] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const s = await api.settings.get(false);
        setSettings(s);
        setStartersText((s.starter_questions || []).join("\n"));
        setOriginsText((s.allowed_origins || []).join("\n"));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed");
      }
    })();
  }, []);

  async function onSave(e: FormEvent) {
    e.preventDefault();
    if (!settings) return;
    setBusy(true);
    setError("");
    setSaved("");
    try {
      const updated = await api.settings.update({
        bot_name: settings.bot_name,
        primary_color: settings.primary_color,
        welcome_message: settings.welcome_message,
        starter_questions: startersText
          .split("\n")
          .map((s) => s.trim())
          .filter(Boolean),
        allowed_origins: originsText
          .split("\n")
          .map((s) => s.trim())
          .filter(Boolean),
        rate_limit_rpm: settings.rate_limit_rpm,
        webhook_url: settings.webhook_url || "",
      });
      setSettings(updated);
      setStartersText((updated.starter_questions || []).join("\n"));
      setOriginsText((updated.allowed_origins || []).join("\n"));
      setSaved("Saved. Widget config will pick this up on next load.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setBusy(false);
    }
  }

  async function revealKey() {
    const s = await api.settings.get(true);
    setRevealedKey(s.api_key);
  }

  async function copySnippet() {
    if (!settings) return;
    await navigator.clipboard.writeText(settings.embed_snippet);
    setSaved("Embed snippet copied.");
  }

  if (!settings) {
    return (
      <section className="page">
        <h1 className="page-title">Settings</h1>
        <p className="muted">{error || "Loading…"}</p>
      </section>
    );
  }

  return (
    <section className="page">
      <h1 className="page-title">Settings</h1>
      <p className="page-blurb">
        Branding, origins, and embed code for {settings.business_name}.
      </p>
      {error ? <div className="error">{error}</div> : null}
      {saved ? <div className="success">{saved}</div> : null}

      <form className="panel stack" onSubmit={onSave}>
        <label className="field">
          <span>Bot name</span>
          <input
            value={settings.bot_name}
            onChange={(e) => setSettings({ ...settings, bot_name: e.target.value })}
            required
          />
        </label>
        <label className="field">
          <span>Primary color</span>
          <input
            value={settings.primary_color}
            onChange={(e) => setSettings({ ...settings, primary_color: e.target.value })}
            required
          />
        </label>
        <label className="field">
          <span>Welcome message</span>
          <textarea
            rows={3}
            value={settings.welcome_message}
            onChange={(e) => setSettings({ ...settings, welcome_message: e.target.value })}
            required
          />
        </label>
        <label className="field">
          <span>Starter questions (one per line)</span>
          <textarea rows={4} value={startersText} onChange={(e) => setStartersText(e.target.value)} />
        </label>
        <label className="field">
          <span>Allowed origins (one per line)</span>
          <textarea rows={4} value={originsText} onChange={(e) => setOriginsText(e.target.value)} />
        </label>
        <label className="field">
          <span>Rate limit (requests / minute)</span>
          <input
            type="number"
            min={1}
            value={settings.rate_limit_rpm}
            onChange={(e) =>
              setSettings({ ...settings, rate_limit_rpm: Number(e.target.value) || 60 })
            }
          />
        </label>
        <label className="field">
          <span>Webhook URL (optional)</span>
          <input
            value={settings.webhook_url || ""}
            onChange={(e) => setSettings({ ...settings, webhook_url: e.target.value })}
            placeholder="https://hooks.slack.com/..."
          />
        </label>
        <button className="btn primary" type="submit" disabled={busy}>
          {busy ? "Saving…" : "Save settings"}
        </button>
      </form>

      <div className="panel stack">
        <h2 className="section-title">API key</h2>
        <p className="muted">Masked: {settings.api_key_masked}</p>
        {revealedKey ? (
          <code className="mono-block">{revealedKey}</code>
        ) : (
          <button type="button" className="btn ghost" onClick={() => void revealKey()}>
            Reveal API key
          </button>
        )}
      </div>

      <div className="panel stack">
        <h2 className="section-title">Embed snippet</h2>
        <p className="muted">
          Replace YOUR_API_HOST / YOUR_CDN for production. For local widget build use
          widget/dist/widget.js and http://localhost:8000.
        </p>
        <pre className="mono-block">{settings.embed_snippet}</pre>
        <button type="button" className="btn primary" onClick={() => void copySnippet()}>
          Copy snippet
        </button>
      </div>
    </section>
  );
}
