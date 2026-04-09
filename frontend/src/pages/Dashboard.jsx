import { useEffect, useState } from "react";

import DocumentCard from "../components/DocumentCard";
import SearchBar from "../components/SearchBar";
import api from "../services/api";

export default function Dashboard() {
  // Load and display document summaries for the signed-in user.
  const [documents, setDocuments] = useState([]);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const loadDocuments = async () => {
    // Fetch the current document list, optionally filtered by type.
    try {
      setLoading(true);
      const response = await api.get("/documents", {
        params: filter ? { document_type: filter } : {}
      });
      setDocuments(response.data.data);
    } catch (loadError) {
      setError(loadError.response?.data?.error || "Failed to load documents.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, [filter]);

  const handleSearch = async (event) => {
    // Run a server-side search against document metadata and OCR text.
    event.preventDefault();
    if (!query.trim()) {
      loadDocuments();
      return;
    }
    try {
      const response = await api.get("/documents/search", {
        params: filter ? { q: query, document_type: filter } : { q: query }
      });
      setDocuments(response.data.data);
    } catch (searchError) {
      setError(searchError.response?.data?.error || "Search failed.");
    }
  };

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-ember">Dashboard</p>
          <h1 className="font-display text-4xl text-ink">Your processed documents</h1>
        </div>
        <select
          value={filter}
          onChange={(event) => setFilter(event.target.value)}
          className="rounded-2xl border border-ink/10 bg-white px-4 py-3"
        >
          <option value="">All document types</option>
          <option value="invoice">Invoice</option>
          <option value="resume">Resume</option>
          <option value="contract">Contract</option>
        </select>
      </div>
      <SearchBar value={query} onChange={setQuery} onSubmit={handleSearch} />
      {error ? <p className="mt-4 text-sm text-rose-600">{error}</p> : null}
      {loading ? <p className="mt-4 text-sm text-ink/60">Loading documents...</p> : null}
      <div className="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {documents.map((document) => (
          <DocumentCard key={document.id} document={document} />
        ))}
      </div>
      {!documents.length ? <p className="mt-8 text-ink/60">No documents found yet.</p> : null}
    </div>
  );
}
