import { createContext, useEffect, useState } from "react";

import api from "../services/api";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // Manage the authenticated user and JWT token for the app shell.
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Restore the active session from local storage on first load.
    const token = localStorage.getItem("dis_token");
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .get("/users/me")
      .then((response) => {
        setUser(response.data.data);
      })
      .catch(() => {
        localStorage.removeItem("dis_token");
        setUser(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const login = async (email, password, mode = "login") => {
    // Authenticate or register the current user and persist the returned token.
    const endpoint = mode === "register" ? "/users/register" : "/users/login";
    const response = await api.post(endpoint, { email, password });
    localStorage.setItem("dis_token", response.data.data.access_token);
    setUser(response.data.data.user);
  };

  const logout = () => {
    // Clear the active session from both memory and local storage.
    localStorage.removeItem("dis_token");
    setUser(null);
  };

  return <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>;
}
