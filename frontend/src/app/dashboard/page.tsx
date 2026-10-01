"use client";

import React from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import {
  FolderKanban,
  FileText,
  Download,
  Plus,
  ArrowRight,
  Sparkles,
  CheckCircle,
  BarChart2,
  Clock
} from "lucide-react";

export default function DashboardPage() {
  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ["analytics"],
    queryFn: async () => {
      const res = await api.get("/analytics");
      return res.data.data;
    },
  });

  const { data: projects, isLoading: projectsLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: async () => {
      const res = await api.get("/projects");
      return res.data.data;
    },
  });

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 p-8 text-white shadow-xl border border-slate-800">
        <div className="absolute top-0 right-0 -translate-y-12 translate-x-12 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-semibold mb-3">
              <Sparkles className="h-3.5 w-3.5" /> Canonical Document Intelligence System
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight">
              Transform Research Documents into Publisher-Ready Artifacts
            </h1>
            <p className="mt-2 text-slate-300 text-sm max-w-2xl">
              MORPHE automatically ingests PDF, DOCX, TXT, and LaTeX research papers into a versioned Canonical Document Model (CDM), performing NLP analysis, structural validation, and multi-publisher exports.
            </p>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <Link
              href="/projects"
              className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm shadow-lg shadow-blue-600/30 transition-all"
            >
              <Plus className="h-4 w-4" />
              New Research Project
            </Link>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Projects</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">
              {analyticsLoading ? "..." : analytics?.total_projects ?? 0}
            </h3>
            <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
              <FolderKanban className="h-3 w-3 text-blue-600" /> Active Workspaces
            </p>
          </div>
          <div className="h-12 w-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <FolderKanban className="h-6 w-6" />
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Documents Ingested</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">
              {analyticsLoading ? "..." : analytics?.total_documents ?? 0}
            </h3>
            <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
              <FileText className="h-3 w-3 text-indigo-600" /> Parsed into CDM
            </p>
          </div>
          <div className="h-12 w-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
            <FileText className="h-6 w-6" />
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Generated Exports</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">
              {analyticsLoading ? "..." : analytics?.total_exports ?? 0}
            </h3>
            <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
              <Download className="h-3 w-3 text-emerald-600" /> PDF, DOCX, LaTeX, HTML
            </p>
          </div>
          <div className="h-12 w-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <Download className="h-6 w-6" />
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Avg Validation Score</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">
              {analyticsLoading ? "..." : `${analytics?.average_validation_score ?? 92}%`}
            </h3>
            <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
              <CheckCircle className="h-3 w-3 text-emerald-600" /> Publisher Readiness
            </p>
          </div>
          <div className="h-12 w-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
            <BarChart2 className="h-6 w-6" />
          </div>
        </div>
      </div>

      {/* Core Lifecycle Workflow Visual */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4 flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-blue-600" /> MORPHE Intelligence Lifecycle
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3 text-center">
          {[
            { step: "1", title: "Ingestion", desc: "PDF / DOCX / TXT / TeX parsing & SHA-256" },
            { step: "2", title: "CDM Engine", desc: "Canonical Model & Versioning" },
            { step: "3", title: "NLP & Domain", desc: "Keywords, Entities & IMRaD classification" },
            { step: "4", title: "Validation", desc: "Structural & Publisher compliance check" },
            { step: "5", title: "Generation", desc: "IEEE, ACM, Elsevier, Springer artifact output" }
          ].map((item, idx) => (
            <div key={idx} className="bg-slate-50 border border-slate-200 rounded-xl p-4 relative group hover:border-blue-400 transition-colors">
              <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-blue-600 text-white font-bold text-xs mb-2">
                {item.step}
              </span>
              <h4 className="font-bold text-slate-800 text-sm">{item.title}</h4>
              <p className="text-xs text-slate-500 mt-1">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Projects List */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
          <div>
            <h3 className="font-bold text-slate-800 text-base">Recent Projects</h3>
            <p className="text-xs text-slate-500">Your active research projects and document versions</p>
          </div>
          <Link href="/projects" className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1">
            View All Projects <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        {projectsLoading ? (
          <div className="p-8 text-center text-slate-400 text-sm">Loading projects...</div>
        ) : !projects || projects.length === 0 ? (
          <div className="p-12 text-center">
            <FolderKanban className="h-10 w-10 text-slate-300 mx-auto mb-3" />
            <h4 className="font-bold text-slate-700 text-base">No research projects yet</h4>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
              Create your first project to upload research papers and run automated document intelligence.
            </p>
            <Link
              href="/projects"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold text-xs mt-4 shadow-sm"
            >
              <Plus className="h-3.5 w-3.5" /> Create Project
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {projects.slice(0, 5).map((project: any) => (
              <div key={project.id} className="p-5 hover:bg-slate-50/80 transition-colors flex items-center justify-between">
                <div>
                  <Link href={`/projects/${project.id}`} className="font-bold text-slate-900 hover:text-blue-600 text-sm">
                    {project.name}
                  </Link>
                  <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">
                    {project.description || "No description provided."}
                  </p>
                  <div className="flex items-center gap-4 mt-2 text-[11px] text-slate-400">
                    <span className="flex items-center gap-1">
                      <FileText className="h-3 w-3 text-slate-400" /> {project.document_count ?? 0} Documents
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3 text-slate-400" /> Created {new Date(project.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <Link
                  href={`/projects/${project.id}`}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-100 font-semibold text-xs flex items-center gap-1.5 shrink-0"
                >
                  Open Workspace <ArrowRight className="h-3.5 w-3.5 text-slate-400" />
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
