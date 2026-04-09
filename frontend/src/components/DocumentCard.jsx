import { Link } from "react-router-dom";

export default function DocumentCard({ document }) {
  // Present a compact document summary for dashboard lists.
  const badgeStyles = {
    pending: "bg-amber-100 text-amber-700",
    processing: "bg-sky-100 text-sky-700",
    completed: "bg-emerald-100 text-emerald-700",
    failed: "bg-rose-100 text-rose-700"
  };

  return (
    <Link
      to={`/documents/${document.id}`}
      className="rounded-3xl bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-md"
    >
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-ink">{document.filename}</h3>
          <p className="text-sm text-ink/60">{document.document_type || "Unknown type"}</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-medium ${badgeStyles[document.status] || badgeStyles.pending}`}>
          {document.status}
        </span>
      </div>
      <p className="text-sm text-ink/70">Uploaded {new Date(document.uploaded_at).toLocaleString()}</p>
      {document.processing_error ? <p className="mt-3 text-sm text-rose-600">{document.processing_error}</p> : null}
    </Link>
  );
}
