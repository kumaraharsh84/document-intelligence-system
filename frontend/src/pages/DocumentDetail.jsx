import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import ExtractedDataTable from "../components/ExtractedDataTable";
import api from "../services/api";

export default function DocumentDetail() {
  // Load one document and allow the user to trigger extraction.
  const { id } = useParams();
  const [document, setDocument] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadDocument = async () => {
    // Fetch the selected document and its extraction data.
    try {
      const response = await api.get(`/documents/${id}`);
      setDocument(response.data.data);
    } catch (loadError) {
      setError(loadError.response?.data?.error || "Failed to load document.");
    }
  };

  useEffect(() => {
    loadDocument();
  }, [id]);

  useEffect(() => {
    // Poll the document while extraction is still running so the page updates automatically.
    if (!document || document.status !== "processing") {
      return undefined;
    }
    const timer = setInterval(() => {
      loadDocument();
    }, 3000);
    return () => clearInterval(timer);
  }, [document?.status, id]);

  const triggerExtraction = async () => {
    // Call the backend extraction endpoint for the selected document.
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const response = await api.post(`/documents/${id}/extract`, { document_type_hint: document?.document_type || null });
      setMessage(response.data.message || "Extraction queued.");
      await loadDocument();
    } catch (extractError) {
      setError(extractError.response?.data?.error || "Extraction failed.");
    } finally {
      setBusy(false);
    }
  };

  if (!document) {
    return <div className="mx-auto max-w-5xl px-6 py-8 text-ink/70">{error || "Loading document..."}</div>;
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-8">
      <div className="mb-6 flex flex-col gap-4 rounded-[2rem] bg-white p-6 shadow-sm md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-ember">Document detail</p>
          <h1 className="font-display text-4xl text-ink">{document.filename}</h1>
          <p className="mt-2 text-ink/60">
            Status: {document.status} | Type: {document.document_type || "Unknown"}
          </p>
          {document.processing_started_at ? (
            <p className="mt-1 text-sm text-ink/50">
              Started: {new Date(document.processing_started_at).toLocaleString()}
            </p>
          ) : null}
          {document.processing_completed_at ? (
            <p className="mt-1 text-sm text-ink/50">
              Completed: {new Date(document.processing_completed_at).toLocaleString()}
            </p>
          ) : null}
        </div>
        <button type="button" onClick={triggerExtraction} disabled={busy} className="rounded-full bg-ink px-6 py-3 font-medium text-white">
          {busy ? "Submitting..." : document.status === "processing" ? "Processing..." : "Run Extraction"}
        </button>
      </div>
      {message ? <p className="mb-4 text-sm text-emerald-700">{message}</p> : null}
      {error ? <p className="mb-4 text-sm text-rose-600">{error}</p> : null}
      {document.processing_error ? <p className="mb-4 text-sm text-rose-600">{document.processing_error}</p> : null}
      <ExtractedDataTable data={document.extracted_data} />
    </div>
  );
}
