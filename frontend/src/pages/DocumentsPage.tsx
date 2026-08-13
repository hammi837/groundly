import { useCallback, useEffect, useState, type FormEvent } from "react";
import { api } from "../lib/api";
import type { Document } from "../types";

type EditState = {
  id: string;
  source_type: string;
  source_name: string;
  question: string;
  answer: string;
};

export function DocumentsPage() {
  const [docs, setDocs] = useState<Document[]>([]);
  const [error, setError] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [busy, setBusy] = useState(false);
  const [edit, setEdit] = useState<EditState | null>(null);
  const [editBusy, setEditBusy] = useState(false);
  const [editError, setEditError] = useState("");

  const load = useCallback(async () => {
    try {
      setDocs(await api.documents.list());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load documents");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    const processing = docs.some((d) => d.status === "processing");
    if (!processing) return;
    const id = window.setInterval(() => void load(), 2000);
    return () => window.clearInterval(id);
  }, [docs, load]);

  async function onUpload(file: File | null) {
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      await api.documents.upload(file);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  async function onFaq(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.documents.faq({ question, answer });
      setQuestion("");
      setAnswer("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "FAQ failed");
    } finally {
      setBusy(false);
    }
  }

  async function onDelete(id: string) {
    if (!confirm("Delete this document and its chunks?")) return;
    await api.documents.remove(id);
    await load();
  }

  async function openEdit(doc: Document) {
    setEditError("");
    setEditBusy(true);
    try {
      const content = await api.documents.content(doc.id);
      setEdit({
        id: doc.id,
        source_type: doc.source_type,
        source_name: content.source_name,
        question: content.question || "",
        answer: content.answer || "",
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load document");
    } finally {
      setEditBusy(false);
    }
  }

  async function saveEdit(e: FormEvent) {
    e.preventDefault();
    if (!edit) return;
    setEditBusy(true);
    setEditError("");
    try {
      if (edit.source_type === "faq") {
        await api.documents.update(edit.id, {
          source_name: edit.source_name,
          question: edit.question,
          answer: edit.answer,
        });
      } else {
        await api.documents.update(edit.id, { source_name: edit.source_name });
      }
      setEdit(null);
      await load();
    } catch (err) {
      setEditError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setEditBusy(false);
    }
  }

  async function replacePdf(file: File | null) {
    if (!edit || !file) return;
    setEditBusy(true);
    setEditError("");
    try {
      await api.documents.replacePdf(edit.id, file);
      setEdit(null);
      await load();
    } catch (err) {
      setEditError(err instanceof Error ? err.message : "Replace failed");
    } finally {
      setEditBusy(false);
    }
  }

  return (
    <section className="page">
      <h1 className="page-title">Documents</h1>
      <p className="page-blurb">
        Upload PDFs or add FAQ pairs. Processing runs in the background. Sample site PDF:{" "}
        <code>demo/riverside-patient-faq.pdf</code>
      </p>
      {error ? <div className="error">{error}</div> : null}

      <div className="panel-grid">
        <div className="panel">
          <h2 className="section-title">Upload PDF</h2>
          <label className="upload-zone">
            <input
              type="file"
              accept="application/pdf,.pdf"
              disabled={busy}
              onChange={(e) => void onUpload(e.target.files?.[0] || null)}
            />
            <span>Drop a PDF or click to browse</span>
          </label>
        </div>
        <div className="panel">
          <h2 className="section-title">Add FAQ</h2>
          <form className="stack" onSubmit={onFaq}>
            <label className="field">
              <span>Question</span>
              <input value={question} onChange={(e) => setQuestion(e.target.value)} required />
            </label>
            <label className="field">
              <span>Answer</span>
              <textarea value={answer} onChange={(e) => setAnswer(e.target.value)} rows={4} required />
            </label>
            <button className="btn primary" type="submit" disabled={busy}>
              Add FAQ
            </button>
          </form>
        </div>
      </div>

      <h2 className="section-title">Library</h2>
      {docs.length === 0 ? (
        <div className="empty-state">No documents yet — upload a PDF or add an FAQ.</div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Status</th>
              <th>Chunks</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {docs.map((d) => (
              <tr key={d.id}>
                <td>
                  <div className="strong">{d.source_name}</div>
                  {d.error_message ? <div className="error tiny">{d.error_message}</div> : null}
                </td>
                <td>{d.source_type}</td>
                <td>
                  <span className={`status ${d.status}`}>{d.status}</span>
                </td>
                <td>{d.chunk_count}</td>
                <td className="row-actions">
                  <button
                    type="button"
                    className="btn ghost small"
                    disabled={editBusy}
                    onClick={() => void openEdit(d)}
                  >
                    Edit
                  </button>
                  <button type="button" className="btn ghost small" onClick={() => void onDelete(d.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {edit ? (
        <div className="modal-backdrop" role="presentation" onClick={() => !editBusy && setEdit(null)}>
          <div
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="edit-doc-title"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 id="edit-doc-title" className="section-title">
              Edit {edit.source_type === "faq" ? "FAQ" : "PDF"}
            </h2>
            {editError ? <div className="error">{editError}</div> : null}
            <form className="stack" onSubmit={saveEdit}>
              <label className="field">
                <span>Name</span>
                <input
                  value={edit.source_name}
                  onChange={(e) => setEdit({ ...edit, source_name: e.target.value })}
                  required
                />
              </label>
              {edit.source_type === "faq" ? (
                <>
                  <label className="field">
                    <span>Question</span>
                    <input
                      value={edit.question}
                      onChange={(e) => setEdit({ ...edit, question: e.target.value })}
                      required
                    />
                  </label>
                  <label className="field">
                    <span>Answer</span>
                    <textarea
                      value={edit.answer}
                      onChange={(e) => setEdit({ ...edit, answer: e.target.value })}
                      rows={5}
                      required
                    />
                  </label>
                </>
              ) : (
                <label className="field">
                  <span>Replace PDF file</span>
                  <input
                    type="file"
                    accept="application/pdf,.pdf"
                    disabled={editBusy}
                    onChange={(e) => void replacePdf(e.target.files?.[0] || null)}
                  />
                </label>
              )}
              <div className="row-actions">
                <button className="btn primary" type="submit" disabled={editBusy}>
                  Save
                </button>
                <button
                  className="btn ghost"
                  type="button"
                  disabled={editBusy}
                  onClick={() => setEdit(null)}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </section>
  );
}
