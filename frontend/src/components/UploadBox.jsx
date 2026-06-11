import { useRef, useState } from "react";

export default function UploadBox({ onFileSelect, busy }) {
  // Render a drag-and-drop upload box with file validation hints.
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFiles = (files) => {
    // Pass the selected files back to the parent page.
    if (files && files.length > 0) {
      onFileSelect(Array.from(files));
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
      className={`relative overflow-hidden rounded-[2.5rem] border-2 border-dashed p-16 text-center transition-all duration-300 ${
        isDragging 
          ? "border-indigo-500 bg-indigo-50/50 shadow-[0_0_40px_rgba(99,102,241,0.2)]" 
          : "border-slate-200 bg-white/50 hover:border-indigo-300 hover:bg-slate-50/50 hover:shadow-md"
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".doc,.docx,.xls,.xlsx,.pdf,.png,.jpg,.jpeg,.webp"
        multiple
        className="hidden"
        onChange={(event) => handleFiles(event.target.files)}
      />
      
      <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-indigo-100 text-indigo-600 shadow-inner">
        <svg xmlns="http://www.w3.org/2000/svg" className={`h-10 w-10 transition-transform duration-300 ${isDragging ? "-translate-y-2" : ""}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="17 8 12 3 7 8"></polyline>
          <line x1="12" y1="3" x2="12" y2="15"></line>
        </svg>
      </div>

      <h2 className="font-display text-4xl font-semibold text-slate-800">
        Drag & drop your files here
      </h2>
      <p className="mt-4 text-lg text-slate-500">
        Supports PDF, PNG, JPG, JPEG, WEBP, DOCX, XLSX (up to 10MB)
      </p>
      
      <div className="mt-10 flex items-center justify-center gap-4">
        <div className="h-px flex-1 bg-slate-200"></div>
        <span className="text-sm font-medium uppercase tracking-wider text-slate-400">or</span>
        <div className="h-px flex-1 bg-slate-200"></div>
      </div>

      <button
        type="button"
        disabled={busy}
        onClick={() => inputRef.current?.click()}
        className="relative mt-10 overflow-hidden rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 px-10 py-4 text-lg font-bold text-white shadow-lg shadow-indigo-500/30 transition-all hover:-translate-y-1 hover:shadow-indigo-500/50 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-70 disabled:hover:translate-y-0"
      >
        <div className="absolute inset-0 flex h-full w-full justify-center [transform:skew(-12deg)_translateX(-100%)] group-hover:duration-1000 group-hover:[transform:skew(-12deg)_translateX(100%)]">
          <div className="relative h-full w-8 bg-white/20"></div>
        </div>
        {busy ? "Uploading..." : "Browse Files"}
      </button>
    </div>
  );
}
