import { useState } from "react";

import UploadBox from "../components/UploadBox";
import api from "../services/api";

export default function UploadPage() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const uploadFiles = async () => {
    if (!selectedFiles.length) {
      setError("Choose at least one file before uploading.");
      return;
    }
    const formData = new FormData();
    selectedFiles.forEach((file) => formData.append("files", file));
    
    setBusy(true);
    setMessage("");
    setError("");
    try {
      const response = await api.post("/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setMessage(`Successfully uploaded ${response.data.data.length} document(s).`);
      setSelectedFiles([]);
    } catch (uploadError) {
      setError(uploadError.response?.data?.error || "Upload failed.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <div className="mb-10 text-center">
        <p className="mb-3 text-sm font-bold uppercase tracking-widest text-indigo-500">Document Processing</p>
        <h1 className="font-display text-5xl font-extrabold text-slate-900 tracking-tight">Upload Your Documents</h1>
        <p className="mt-4 text-lg text-slate-500 max-w-2xl mx-auto">
          Securely upload your invoices, resumes, or contracts. Our AI will automatically extract the key structured data for you.
        </p>
      </div>

      <UploadBox onFileSelect={setSelectedFiles} busy={busy} />
      
      {selectedFiles.length > 0 && (
        <div className="mt-8 rounded-3xl bg-white p-8 shadow-xl shadow-slate-200/50 border border-slate-100">
          <div className="mb-6 flex items-center justify-between border-b border-slate-100 pb-4">
            <h3 className="font-display text-2xl font-bold text-slate-800">
              Ready to upload
            </h3>
            <span className="rounded-full bg-indigo-100 px-3 py-1 text-sm font-bold text-indigo-700">
              {selectedFiles.length} file(s)
            </span>
          </div>
          
          <ul className="mb-8 max-h-60 overflow-y-auto pr-2 space-y-3">
            {selectedFiles.map((file, idx) => (
              <li key={idx} className="flex items-center gap-4 rounded-xl bg-slate-50 px-5 py-4 transition-colors hover:bg-slate-100">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white text-indigo-500 shadow-sm">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                    <polyline points="13 2 13 9 20 9"></polyline>
                  </svg>
                </div>
                <div className="flex-1 truncate">
                  <p className="truncate font-medium text-slate-700">{file.name}</p>
                  <p className="text-sm text-slate-400">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </li>
            ))}
          </ul>

          <button 
            type="button" 
            onClick={uploadFiles} 
            disabled={busy} 
            className="group flex w-full items-center justify-center gap-3 rounded-2xl bg-emerald-500 px-8 py-5 text-xl font-bold text-white shadow-lg shadow-emerald-500/30 transition-all hover:-translate-y-1 hover:bg-emerald-400 hover:shadow-emerald-500/50 disabled:opacity-70 disabled:hover:translate-y-0"
          >
            {busy ? (
              <>
                <svg className="h-6 w-6 animate-spin text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 transition-transform group-hover:-translate-y-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="12" y1="19" x2="12" y2="5"></line>
                  <polyline points="5 12 12 5 19 12"></polyline>
                </svg>
                Confirm & Upload {selectedFiles.length} Document(s)
              </>
            )}
          </button>
        </div>
      )}
      
      {message && (
        <div className="mt-8 rounded-2xl bg-emerald-50 p-6 text-center shadow-sm border border-emerald-100">
          <p className="text-lg font-semibold text-emerald-700">{message}</p>
        </div>
      )}
      
      {error && (
        <div className="mt-8 rounded-2xl bg-rose-50 p-6 text-center shadow-sm border border-rose-100">
          <p className="text-lg font-semibold text-rose-700">{error}</p>
        </div>
      )}
    </div>
  );
}
