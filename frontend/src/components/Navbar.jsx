import { useContext, useState } from "react";
import { Link, NavLink } from "react-router-dom";

import { AuthContext } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useContext(AuthContext);
  const [showDropdown, setShowDropdown] = useState(false);

  // Extract initial from email for the avatar
  const userInitial = user?.email ? user.email.charAt(0).toUpperCase() : "?";

  return (
    <nav className="sticky top-0 z-50 border-b border-white/20 bg-white/60 backdrop-blur-md shadow-sm">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 group">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-500/30 transition-transform group-hover:scale-105">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
          </div>
          <span className="font-display text-2xl font-bold tracking-tight text-slate-900">
            Doc<span className="text-indigo-600">Intel</span>
          </span>
        </Link>

        {/* Navigation Actions */}
        <div className="flex items-center gap-6">
          <NavLink 
            to="/dashboard" 
            className={({isActive}) => `text-sm font-medium transition-colors ${isActive ? "text-indigo-600" : "text-slate-600 hover:text-slate-900"}`}
          >
            Dashboard
          </NavLink>

          <div className="h-6 w-px bg-slate-200"></div>

          {/* Primary CTA: Upload */}
          <NavLink 
            to="/upload" 
            className={({isActive}) => `flex items-center gap-2 rounded-full px-5 py-2.5 text-sm font-semibold transition-all shadow-sm ${
              isActive 
                ? "bg-indigo-700 text-white shadow-indigo-700/20" 
                : "bg-indigo-600 text-white shadow-indigo-600/20 hover:bg-indigo-500 hover:shadow-md hover:-translate-y-0.5"
            }`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            Upload Document
          </NavLink>

          {/* User Profile Dropdown */}
          <div className="relative">
            <button 
              onClick={() => setShowDropdown(!showDropdown)}
              onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
              className="flex items-center gap-3 rounded-full border border-slate-200 bg-white p-1 pr-3 shadow-sm transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-100 text-sm font-bold text-slate-700">
                {userInitial}
              </div>
              <svg xmlns="http://www.w3.org/2000/svg" className={`h-4 w-4 text-slate-500 transition-transform ${showDropdown ? "rotate-180" : ""}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </button>

            {/* Dropdown Menu */}
            {showDropdown && (
              <div className="absolute right-0 mt-2 w-56 origin-top-right rounded-2xl border border-slate-100 bg-white p-2 shadow-xl ring-1 ring-black/5 animate-in fade-in slide-in-from-top-2 duration-200">
                <div className="px-3 py-2">
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Signed in as</p>
                  <p className="truncate text-sm font-semibold text-slate-900 mt-0.5">{user?.email}</p>
                </div>
                <div className="my-1 border-t border-slate-100"></div>
                <button
                  onClick={logout}
                  className="flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-sm font-medium text-rose-600 transition hover:bg-rose-50"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                    <polyline points="16 17 21 12 16 7"></polyline>
                    <line x1="21" y1="12" x2="9" y2="12"></line>
                  </svg>
                  Sign Out
                </button>
              </div>
            )}
          </div>

        </div>
      </div>
    </nav>
  );
}
