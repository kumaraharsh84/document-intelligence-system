export default function ExtractedDataTable({ data }) {
  // Render structured extraction fields for a single document.
  const fields = data?.structured_json?.extracted_fields || {};
  const documentType = data?.structured_json?.document_type;

  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-xl font-semibold text-ink">Extracted Data</h2>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl bg-sand p-4">
          <p className="text-sm text-ink/60">Name</p>
          <p className="font-medium">{fields.name || "-"}</p>
        </div>
        <div className="rounded-2xl bg-sand p-4">
          <p className="text-sm text-ink/60">Date</p>
          <p className="font-medium">{fields.date || "-"}</p>
        </div>
        <div className="rounded-2xl bg-sand p-4">
          <p className="text-sm text-ink/60">Amount</p>
          <p className="font-medium">{fields.amount ?? "-"}</p>
        </div>
        <div className="rounded-2xl bg-sand p-4">
          <p className="text-sm text-ink/60">Vendor</p>
          <p className="font-medium">{fields.vendor || "-"}</p>
        </div>
      </div>
      <div className="mt-4 rounded-2xl bg-sand p-4">
        <p className="text-sm text-ink/60">Keywords</p>
        <p className="mt-2">{(fields.keywords || []).join(", ") || "-"}</p>
      </div>
      {fields.summary ? (
        <div className="mt-4 rounded-2xl bg-mist p-4">
          <p className="text-sm text-ink/60">Summary</p>
          <p className="mt-2">{fields.summary}</p>
        </div>
      ) : null}
      {documentType === "resume" ? (
        <div className="mt-4 rounded-2xl bg-sand p-4">
          <p className="text-sm text-ink/60">Skills</p>
          <p className="mt-2">{(fields.skills || []).join(", ") || "-"}</p>
        </div>
      ) : null}
      {documentType === "contract" ? (
        <div className="mt-4 rounded-2xl bg-sand p-4">
          <p className="text-sm text-ink/60">Parties</p>
          <p className="mt-2">{(fields.parties || []).join(", ") || "-"}</p>
        </div>
      ) : null}
      {documentType === "invoice" ? (
        <div className="mt-4 rounded-2xl bg-sand p-4">
          <p className="text-sm text-ink/60">Line Items</p>
          <div className="mt-2 space-y-2">
            {(fields.line_items || []).length ? (
              (fields.line_items || []).map((item, index) => (
                <div key={`${item.description || "line"}-${index}`} className="rounded-xl bg-white px-3 py-2 text-sm">
                  {item.description || JSON.stringify(item)}
                </div>
              ))
            ) : (
              <p>-</p>
            )}
          </div>
        </div>
      ) : null}
      <div className="mt-4 rounded-2xl bg-white ring-1 ring-ink/10 p-4">
        <p className="text-sm text-ink/60">Confidence Score</p>
        <p className="mt-2 font-medium">{data?.confidence_score ?? "-"}</p>
      </div>
      <div className="mt-4 rounded-2xl bg-ink p-4 text-white">
        <p className="text-sm text-white/70">Raw OCR Text</p>
        <pre className="mt-2 whitespace-pre-wrap text-sm">{data?.raw_text || "No OCR text available yet."}</pre>
      </div>
    </div>
  );
}
