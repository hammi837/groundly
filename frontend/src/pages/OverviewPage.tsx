import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import type { AnalyticsOverview } from "../types";

export function OverviewPage() {
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [unanswered, setUnanswered] = useState<
    { conversation_id: string; question: string; created_at: string }[]
  >([]);
  const [error, setError] = useState("");

  useEffect(() => {
    void (async () => {
      try {
        const [overview, gaps] = await Promise.all([
          api.analytics.overview(),
          api.analytics.unanswered(),
        ]);
        setData(overview);
        setUnanswered(gaps.slice(0, 8));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load");
      }
    })();
  }, []);

  return (
    <section className="page">
      <h1 className="page-title">Overview</h1>
      <p className="page-blurb">
        Snapshot of conversations, content gaps, and ready documents for this tenant.
      </p>
      {error ? <div className="error">{error}</div> : null}
      {data ? (
        <div className="stat-row">
          <div className="stat">
            <div className="stat-value">{data.conversations}</div>
            <div className="stat-label">Conversations</div>
          </div>
          <div className="stat">
            <div className="stat-value">{data.messages}</div>
            <div className="stat-label">Messages</div>
          </div>
          <div className="stat">
            <div className="stat-value">{data.leads}</div>
            <div className="stat-label">Leads</div>
          </div>
          <div className="stat">
            <div className="stat-value">{Math.round(data.fallback_rate * 100)}%</div>
            <div className="stat-label">Fallback rate</div>
          </div>
          <div className="stat">
            <div className="stat-value">{data.documents_ready}</div>
            <div className="stat-label">Docs ready</div>
          </div>
        </div>
      ) : (
        <p className="muted">Loading…</p>
      )}

      <h2 className="section-title">Unanswered (content gaps)</h2>
      {unanswered.length === 0 ? (
        <div className="empty-state">
          No fallback questions yet.{" "}
          <Link to="/documents">Upload docs</Link> or try the widget.
        </div>
      ) : (
        <ul className="gap-list">
          {unanswered.map((item) => (
            <li key={`${item.conversation_id}-${item.created_at}`}>
              <Link to={`/conversations/${item.conversation_id}`}>{item.question}</Link>
              <span className="muted">{new Date(item.created_at).toLocaleString()}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
