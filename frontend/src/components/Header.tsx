"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { Sparkles, FileText, CheckCircle2 } from "lucide-react";

export default function Header() {
  const pathname = usePathname();
  const { user } = useAuth();

  if (pathname === "/login" || pathname === "/register") {
    return null;
  }

  const getTitle = () => {
    if (pathname === "/dashboard") return "Platform Overview";
    if (pathname.startsWith("/projects")) return "Research Projects";
    if (pathname.startsWith("/documents")) return "Document Intelligence Workspace";
    if (pathname.startsWith("/knowledge-base")) return "Publisher Knowledge Base";
    if (pathname.startsWith("/exports")) return "Generated Artifact Exports";
    if (pathname.startsWith("/analytics")) return "Platform Analytics & Metrics";
    return "Workspace";
  };

  return (
    <header className="h-16 border-b border-slate-200 bg-white/80 backdrop-blur-md sticky top-0 z-30 px-8 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <h2 className="text-lg font-bold text-slate-800 tracking-tight">{getTitle()}</h2>
        <span className="hidden sm:inline-flex items-center gap-1 text-[11px] font-medium text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200">
          <Sparkles className="h-3 w-3 text-blue-600" /> Canonical Engine Active
        </span>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden md:flex items-center gap-2 text-xs text-slate-600 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200">
          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
          <span>System Status: <strong>Operational</strong></span>
        </div>
      </div>
    </header>
  );
}
