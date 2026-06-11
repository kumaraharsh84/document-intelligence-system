import { useState } from "react";

import UploadBox from "../components/UploadBox";
import api from "../services/api";

export default function UploadPage() {
  // Handle user uploads and display the latest upload result.
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const uploadFiles = async () => {
    // Send the selected files to the backend upload endpoint.
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
    <div className="mx-auto max-w-4xl px-6 py-8">
      <p className="text-sm uppercase tracking-[0.2em] text-ember">Upload</p>
      <h1 className="mb-8 font-display text-4xl text-ink">Send documents for processing</h1>
      <UploadBox onFileSelect={setSelectedFiles} busy={busy} />
      {selectedFiles.length > 0 ? (
        <div className="mt-4 text-sm text-ink/70">
          <p className="font-medium mb-1">Selected files ({selectedFiles.length}):</p>
          <ul className="list-disc pl-5">
            {selectedFiles.map((file, idx) => (
              <li key={idx}>{file.name}</li>
            ))}
          </ul>
        </div>
      ) : null}
      <button type="button" onClick={uploadFiles} disabled={busy} className="mt-6 rounded-full bg-moss px-6 py-3 font-medium text-white">
        {busy ? "Uploading..." : "Upload Documents"}
      </button>
      {message ? <p className="mt-4 text-sm text-emerald-700">{message}</p> : null}
      {error ? <p className="mt-4 text-sm text-rose-600">{error}</p> : null}
    </div>
  );
}
