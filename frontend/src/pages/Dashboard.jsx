import { useEffect, useState, useMemo } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";

import DocumentCard from "../components/DocumentCard";
import SearchBar from "../components/SearchBar";
import api from "../services/api";

export default function Dashboard() {
  const [documents, setDocuments] = useState([]);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const loadDocuments = async () => {
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
    let ws;
    const connectWs = () => {
      // Connect using the same host but ws:// or wss:// protocol
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const host = window.location.hostname;
      // The API base URL is http://localhost:8000/api usually, so we replace http with ws
      const wsUrl = import.meta.env.VITE_API_BASE_URL 
        ? import.meta.env.VITE_API_BASE_URL.replace(/^http/, "ws") + "/ws"
        : `ws://${host}:8000/api/ws`;

      ws = new WebSocket(wsUrl);

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "document_updated") {
            loadDocuments();
          }
        } catch (e) {
          // ignore parsing errors
        }
      };

      ws.onclose = () => {
        // optionally reconnect after delay
        setTimeout(connectWs, 5000);
      };
    };

    connectWs();

    return () => {
      if (ws) {
        ws.onclose = null;
        ws.close();
      }
    };
  }, []); // Connect once on mount

  useEffect(() => {
    loadDocuments();
  }, [filter]);

  const handleSearch = async (event) => {
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

  const stats = useMemo(() => {
    const statusCounts = { pending: 0, processing: 0, completed: 0, failed: 0 };
    const typeCounts = {};

    documents.forEach((doc) => {
      if (statusCounts[doc.status] !== undefined) statusCounts[doc.status]++;
      const type = doc.document_type || "unknown";
      typeCounts[type] = (typeCounts[type] || 0) + 1;
    });

    const statusData = Object.entries(statusCounts).map(([name, value]) => ({ name, value }));
    const typeData = Object.entries(typeCounts).map(([name, value]) => ({ name, value }));

    return { statusData, typeData };
  }, [documents]);

  const COLORS = ["#0284c7", "#f59e0b", "#10b981", "#e11d48", "#8b5cf6", "#14b8a6"];

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
          className="rounded-2xl border border-ink/10 bg-white px-4 py-3 focus:outline-none"
        >
          <option value="">All document types</option>
          <option value="invoice">Invoice</option>
          <option value="resume">Resume</option>
          <option value="contract">Contract</option>
        </select>
      </div>

      {documents.length > 0 && !loading && !error && (
        <div className="mb-10 grid gap-6 md:grid-cols-2">
          <div className="rounded-[2rem] bg-white p-6 shadow-sm border border-ink/5">
            <h3 className="mb-4 text-center font-display text-xl text-ink">Processing Status</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={stats.statusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                    {stats.statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="rounded-[2rem] bg-white p-6 shadow-sm border border-ink/5">
            <h3 className="mb-4 text-center font-display text-xl text-ink">Document Types</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.typeData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "#475569" }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "#475569" }} />
                  <Tooltip cursor={{ fill: "#f1f5f9" }} />
                  <Bar dataKey="value" fill="#0ea5e9" radius={[4, 4, 0, 0]}>
                    {stats.typeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[(index + 1) % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      <SearchBar value={query} onChange={setQuery} onSubmit={handleSearch} />
      
      {error ? <p className="mt-4 text-sm text-rose-600">{error}</p> : null}
      {loading ? <p className="mt-4 text-sm text-ink/60">Loading documents...</p> : null}
      
      <div className="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {documents.map((document) => (
          <DocumentCard key={document.id} document={document} />
        ))}
      </div>
      {!documents.length && !loading ? <p className="mt-8 text-ink/60">No documents found yet.</p> : null}
    </div>
  );
}
