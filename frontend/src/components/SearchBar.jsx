export default function SearchBar({ value, onChange, onSubmit }) {
  // Render a search field used to query uploaded documents.
  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-3 rounded-3xl bg-white p-4 shadow-sm md:flex-row">
      <input
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Search by filename or OCR text"
        className="flex-1 rounded-2xl border border-ink/10 px-4 py-3 outline-none ring-0 focus:border-moss"
      />
      <button type="submit" className="rounded-2xl bg-moss px-5 py-3 font-medium text-white">
        Search
      </button>
    </form>
  );
}
