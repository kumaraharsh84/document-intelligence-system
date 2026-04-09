import { useContext } from "react";
import { Link, NavLink } from "react-router-dom";

import { AuthContext } from "../context/AuthContext";

export default function Navbar() {
  // Render the main application navigation and logout control.
  const { user, logout } = useContext(AuthContext);

  return (
    <nav className="border-b border-ink/10 bg-white/70 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" className="font-display text-2xl font-semibold text-ink">
          DocIntel
        </Link>
        <div className="flex items-center gap-4 text-sm">
          <NavLink to="/dashboard" className="text-ink/80 hover:text-ink">
            Dashboard
          </NavLink>
          <NavLink to="/upload" className="text-ink/80 hover:text-ink">
            Upload
          </NavLink>
          <span className="hidden text-ink/60 md:inline">{user?.email}</span>
          <button
            type="button"
            onClick={logout}
            className="rounded-full bg-ember px-4 py-2 font-medium text-white transition hover:bg-ember/90"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
