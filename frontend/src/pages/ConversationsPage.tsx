import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../lib/api";
import type { ConversationDetail, ConversationListItem } from "../types";

export function ConversationsPage() {
  const [items, setItems] = useState<ConversationListItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    void (async () => {
      try {
        setItems(await api.conversations.list());
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed");
      }
    })();
  }, []);

  return (
    <section className="page">
      <h1 className="page-title">Conversations</h1>
      <p className="page-blurb">Browse visitor chats and cited sources.</p>
      {error ? <div className="error">{error}</div> : null}
      {items.length === 0 ? (
        <div className="empty-state">No conversations yet — try the embed widget.</div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Visitor</th>
              <th>Messages</th>
              <th>Fallback</th>
              <th>Last activity</th>
            </tr>
          </thead>
          <tbody>
            {items.map((c) => (
              <tr key={c.id}>
                <td>
                  <Link to={`/conversations/${c.id}`}>
                    {c.visitor_email || c.visitor_id.slice(0, 12)}
                  </Link>
                </td>
                <td>{c.message_count}</td>
                <td>{c.had_fallback ? "Yes" : "—"}</td>
                <td>{new Date(c.last_message_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

export function ConversationDetailPage() {
  const { id } = useParams();
  const [detail, setDetail] = useState<ConversationDetail | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    void (async () => {
      try {
        setDetail(await api.conversations.get(id));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed");
      }
    })();
  }, [id]);

  return (
    <section className="page">
      <p className="crumb">
        <Link to="/conversations">Conversations</Link> / detail
      </p>
      <h1 className="page-title">Conversation</h1>
      {error ? <div className="error">{error}</div> : null}
      {!detail ? (
        <p className="muted">Loading…</p>
      ) : (
        <>
          <p className="page-blurb">
            Visitor {detail.visitor_email || detail.visitor_id} · started{" "}
            {new Date(detail.started_at).toLocaleString()}
          </p>
          <div className="transcript">
            {detail.messages.map((m) => (
              <div key={m.id} className={`msg ${m.role}`}>
                <div className="msg-role">
                  {m.role}
                  {m.was_fallback ? <span className="status failed">fallback</span> : null}
                </div>
                <div className="msg-body">{m.content}</div>
                {m.citations?.length ? (
                  <div className="chips">
                    {m.citations.map((c) => (
                      <span key={c.chunk_id} className="chip" title={c.excerpt}>
                        Source: {c.document}
                      </span>
                    ))}
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  );
}
