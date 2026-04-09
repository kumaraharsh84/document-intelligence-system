import { useRef, useState } from "react";

export default function UploadBox({ onFileSelect, busy }) {
  // Render a drag-and-drop upload box with file validation hints.
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFiles = (files) => {
    // Pass the first selected file back to the parent page.
    if (files?.[0]) {
      onFileSelect(files[0]);
    }
  };

  return (
    <div
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setIsDragging(false);
        handleFiles(event.dataTransfer.files);
      }}
      className={`rounded-[2rem] border-2 border-dashed p-10 text-center transition ${
        isDragging ? "border-ember bg-ember/10" : "border-ink/20 bg-white"
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.png,.jpg,.jpeg,.webp"
        className="hidden"
        onChange={(event) => handleFiles(event.target.files)}
      />
      <h2 className="font-display text-3xl text-ink">Drop a document here</h2>
      <p className="mt-3 text-ink/65">PDF, PNG, JPG, JPEG, WEBP up to 10MB</p>
      <button
        type="button"
        disabled={busy}
        onClick={() => inputRef.current?.click()}
        className="mt-6 rounded-full bg-ink px-6 py-3 font-medium text-white"
      >
        {busy ? "Uploading..." : "Choose File"}
      </button>
    </div>
  );
}
