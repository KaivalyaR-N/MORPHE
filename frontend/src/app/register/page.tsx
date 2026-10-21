"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { ArrowRight, AlertCircle, Sparkles } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("RESEARCHER");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(email, password, fullName, role);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  const fillSample = () => {
    const rand = Math.floor(100 + Math.random() * 900);
    setFullName("Dr. Research Scholar");
    setEmail(`scholar${rand}@morphe.org`);
    setPassword("Password123!");
    setError("");
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 text-slate-100 relative overflow-hidden">
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-gradient-to-tr from-blue-600/20 via-indigo-600/20 to-purple-600/10 blur-3xl pointer-events-none rounded-full" />

      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center z-10">
        <div className="mx-auto h-12 w-12 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-xl shadow-blue-500/25 font-black text-2xl">
          M
        </div>
        <h2 className="mt-4 text-3xl font-extrabold tracking-tight text-white">
          Create MORPHE Account
        </h2>
        <p className="mt-2 text-sm text-slate-400">
          Register to begin processing research papers
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md z-10">
        <div className="bg-slate-900/90 border border-slate-800 backdrop-blur-xl py-8 px-6 shadow-2xl rounded-2xl sm:px-10">
          {error && (
            <div className="mb-4 bg-rose-500/10 border border-rose-500/30 text-rose-400 px-4 py-3 rounded-lg text-sm font-medium flex items-center gap-2">
              <AlertCircle className="h-4 w-4 shrink-0 text-rose-400" />
              <span>{error}</span>
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                Full Name
              </label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Dr. Kaivalya Sharma"
                className="mt-1.5 block w-full rounded-lg bg-slate-950 border border-slate-800 px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="kaivalya@university.edu"
                className="mt-1.5 block w-full rounded-lg bg-slate-950 border border-slate-800 px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                Password
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Minimum 6 characters"
                className="mt-1.5 block w-full rounded-lg bg-slate-950 border border-slate-800 px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                Academic Role
              </label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="mt-1.5 block w-full rounded-lg bg-slate-950 border border-slate-800 px-3.5 py-2.5 text-sm text-white focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="RESEARCHER">Primary Researcher</option>
                <option value="REVIEWER">Peer Reviewer / Editor</option>
                <option value="PUBLISHER">Publisher Delegate</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm shadow-lg shadow-blue-600/30 transition-all disabled:opacity-50"
            >
              {loading ? "Creating account..." : "Complete Registration"}
              <ArrowRight className="h-4 w-4" />
            </button>

            <button
              type="button"
              onClick={fillSample}
              className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg bg-slate-800/80 hover:bg-slate-800 text-slate-300 font-medium text-xs border border-slate-700 transition-colors"
            >
              <Sparkles className="h-3.5 w-3.5 text-amber-400" />
              Fill Sample Details
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-slate-800 text-center space-y-3">
            <p className="text-xs text-slate-400">
              Already have an account?{" "}
              <Link href="/login" className="text-blue-400 hover:underline font-semibold">
                Sign in to your account
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
