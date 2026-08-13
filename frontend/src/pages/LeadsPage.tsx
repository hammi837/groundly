import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import type { Lead } from "../types";

export function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [error, setError] = useState("");

  async function load() {
    try {
      setLeads(await api.leads.list());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function setStatus(id: string, status: "new" | "contacted") {
    await api.leads.updateStatus(id, status);
    await load();
  }

  return (
    <section className="page">
      <h1 className="page-title">Leads</h1>
      <p className="page-blurb">
        Visitors who hit a content gap and left contact details via the widget handoff.
      </p>
      {error ? <div className="error">{error}</div> : null}
      {leads.length === 0 ? (
        <div className="empty-state">No leads yet — unanswered questions will land here.</div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Contact</th>
              <th>Question</th>
              <th>Status</th>
              <th>When</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {leads.map((l) => (
              <tr key={l.id}>
                <td>
                  <div className="strong">{l.email}</div>
                  <div className="muted">
                    {[l.name, l.phone].filter(Boolean).join(" · ") || "—"}
                  </div>
                </td>
                <td>{l.question}</td>
                <td>
                  <span className={`status ${l.status === "new" ? "processing" : "ready"}`}>
                    {l.status}
                  </span>
                </td>
                <td>{new Date(l.created_at).toLocaleString()}</td>
                <td className="row-actions">
                  <Link className="btn ghost small" to={`/conversations/${l.conversation_id}`}>
                    Transcript
                  </Link>
                  {l.status === "new" ? (
                    <button
                      type="button"
                      className="btn primary small"
                      onClick={() => void setStatus(l.id, "contacted")}
                    >
                      Mark contacted
                    </button>
                  ) : (
                    <button
                      type="button"
                      className="btn ghost small"
                      onClick={() => void setStatus(l.id, "new")}
                    >
                      Reopen
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
