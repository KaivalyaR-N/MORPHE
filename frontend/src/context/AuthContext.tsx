"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { api } from "@/lib/api";

export interface User {
  id: str;
  email: string;
  full_name: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, full_name: string, role?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem("morphe_token");
    const storedUser = localStorage.getItem("morphe_user");

    if (storedToken && storedUser) {
      setToken(storedToken);
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        localStorage.removeItem("morphe_user");
      }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const res = await api.post("/auth/login", { email, password });
    if (res.data.success) {
      const { access_token, user } = res.data.data;
      setToken(access_token);
      setUser(user);
      localStorage.setItem("morphe_token", access_token);
      localStorage.setItem("morphe_user", JSON.stringify(user));
    } else {
      throw new Error(res.data.error?.message || "Login failed");
    }
  };

  const register = async (email: string, password: string, full_name: string, role: string = "RESEARCHER") => {
    const res = await api.post("/auth/register", { email, password, full_name, role });
    if (res.data.success) {
      const { access_token, user } = res.data.data;
      setToken(access_token);
      setUser(user);
      localStorage.setItem("morphe_token", access_token);
      localStorage.setItem("morphe_user", JSON.stringify(user));
    } else {
      throw new Error(res.data.error?.message || "Registration failed");
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("morphe_token");
    localStorage.removeItem("morphe_user");
    window.location.href = "/login";
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
