import { useState } from "react";

import UploadBox from "../components/UploadBox";
import api from "../services/api";

export default function UploadPage() {
  // Handle user uploads and display the latest upload result.
  const [selectedFile, setSelectedFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const uploadFile = async () => {
    // Send the selected file to the backend upload endpoint.
    if (!selectedFile) {
      setError("Choose a file before uploading.");
      return;
    }
    const formData = new FormData();
    formData.append("file", selectedFile);
    setBusy(true);
    setMessage("");
    setError("");
    try {
      const response = await api.post("/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setMessage(`Uploaded ${response.data.data.filename} successfully.`);
    } catch (uploadError) {
      setError(uploadError.response?.data?.error || "Upload failed.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <p className="text-sm uppercase tracking-[0.2em] text-ember">Upload</p>
      <h1 className="mb-8 font-display text-4xl text-ink">Send a document for processing</h1>
      <UploadBox onFileSelect={setSelectedFile} busy={busy} />
      {selectedFile ? <p className="mt-4 text-sm text-ink/70">Selected file: {selectedFile.name}</p> : null}
      <button type="button" onClick={uploadFile} disabled={busy} className="mt-6 rounded-full bg-moss px-6 py-3 font-medium text-white">
        {busy ? "Uploading..." : "Upload Document"}
      </button>
      {message ? <p className="mt-4 text-sm text-emerald-700">{message}</p> : null}
      {error ? <p className="mt-4 text-sm text-rose-600">{error}</p> : null}
    </div>
  );
}
