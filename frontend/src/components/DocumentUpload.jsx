import { useState, useEffect, useRef } from "react";
import "./DocumentUpload.css";

const API = "http://localhost:5000";

export default function DocumentUpload() {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [message, setMessage] = useState(null); // { type: "success"|"error", text }
  const fileRef = useRef(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const res = await fetch(`${API}/api/documents`);
      const data = await res.json();
      setDocuments(data.documents || []);
    } catch {
      // silently ignore — backend may not be running yet
    }
  };

  const uploadFile = async (file) => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setMessage({ type: "error", text: "Only PDF files are accepted." });
      return;
    }

    setUploading(true);
    setMessage(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API}/api/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      if (!res.ok) throw new Error(data.error || "Upload failed.");

      setMessage({
        type: "success",
        text: `Uploaded "${data.filename}" — ${data.chunk_count} chunks indexed.`,
      });
      fetchDocuments();
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const deleteDoc = async (docId, filename) => {
    if (!window.confirm(`Delete "${filename}" and all its indexed content?`)) return;
    try {
      const res = await fetch(`${API}/api/documents/${docId}`, { method: "DELETE" });
      const data = await res.json();
      setMessage({ type: "success", text: `Deleted "${filename}" (${data.chunks_removed} chunks).` });
      fetchDocuments();
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    uploadFile(file);
  };

  return (
    <div className="docupload">
      <div className="docupload__header">
        <span>📄</span>
        <h2>Document Centre</h2>
      </div>

      {/* Drop zone */}
      <div
        className={`docupload__dropzone${dragOver ? " docupload__dropzone--over" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => fileRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === "Enter" && fileRef.current?.click()}
        aria-label="Drop zone for PDF upload"
      >
        <input
          ref={fileRef}
          type="file"
          accept=".pdf"
          style={{ display: "none" }}
          onChange={(e) => uploadFile(e.target.files[0])}
          aria-hidden="true"
        />
        {uploading ? (
          <p className="docupload__hint">Uploading and indexing…</p>
        ) : (
          <>
            <p className="docupload__icon-big">⬆️</p>
            <p className="docupload__hint">Drag & drop a PDF here, or click to browse</p>
            <p className="docupload__sub">Max 20 MB · PDF only</p>
          </>
        )}
      </div>

      {/* Status message */}
      {message && (
        <div className={`docupload__msg docupload__msg--${message.type}`} role="alert">
          {message.type === "success" ? "✅" : "❌"} {message.text}
        </div>
      )}

      {/* Document list */}
      <div className="docupload__list">
        <div className="docupload__list-header">
          <h3>Indexed Documents</h3>
          <span className="docupload__count">{documents.length}</span>
        </div>

        {documents.length === 0 ? (
          <p className="docupload__empty">No documents uploaded yet.</p>
        ) : (
          <ul aria-label="Uploaded documents">
            {documents.map((doc) => (
              <li key={doc.doc_id} className="docupload__item">
                <span className="docupload__file-icon">📃</span>
                <span className="docupload__filename">{doc.filename}</span>
                <span className="docupload__chunks">{doc.chunk_count} chunks</span>
                <button
                  className="docupload__delete"
                  onClick={() => deleteDoc(doc.doc_id, doc.filename)}
                  aria-label={`Delete ${doc.filename}`}
                >
                  🗑
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
