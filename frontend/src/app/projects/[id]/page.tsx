"use client";

import React, { useState, useRef } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import {
  Upload,
  FileText,
  Clock,
  ArrowRight,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  FileCode,
  FileCheck2,
  FolderKanban
} from "lucide-react";

export default function ProjectDetailPage() {
  const { id: projectId } = useParams();
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");

  const { data: project, isLoading: projectLoading } = useQuery({
    queryKey: ["project", projectId],
    queryFn: async () => {
      const res = await api.get(`/projects/${projectId}`);
      return res.data.data;
    },
  });

  const { data: documents, isLoading: documentsLoading } = useQuery({
    queryKey: ["documents", projectId],
    queryFn: async () => {
      const res = await api.get(`/documents/project/${projectId}`);
      return res.data.data;
    },
  });

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    setUploadError("");

    const formData = new FormData();
    formData.append("project_id", projectId as string);
    formData.append("file", file);

    try {
      const res = await api.post("/documents/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      if (res.data.success) {
        queryClient.invalidateQueries({ queryKey: ["documents", projectId] });
        queryClient.invalidateQueries({ queryKey: ["projects"] });
      }
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || "Document upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  const deleteDocumentMutation = useMutation({
    mutationFn: async (documentId: string) => {
      await api.delete(`/documents/${documentId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents", projectId] });
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const onFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header Info */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-blue-600 mb-1">
            <FolderKanban className="h-3.5 w-3.5" /> Project Workspace
          </div>
          <h1 className="text-2xl font-bold text-slate-900">{project?.name || "Loading..."}</h1>
          <p className="text-slate-500 text-xs mt-1">{project?.description || "No description provided."}</p>
        </div>
        <div className="text-right text-xs text-slate-400">
          <p>Created: {project ? new Date(project.created_at).toLocaleDateString() : "-"}</p>
          <p className="font-semibold text-slate-700 mt-0.5">{documents?.length ?? 0} Ingested Documents</p>
        </div>
      </div>

      {/* Drag and Drop File Upload Area */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={onDrop}
        className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all bg-white shadow-sm ${
          isUploading
            ? "border-blue-500 bg-blue-50/50"
            : "border-slate-300 hover:border-blue-400 hover:bg-slate-50/60"
        }`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={onFileSelect}
          accept=".pdf,.docx,.doc,.txt,.md,.tex"
          className="hidden"
        />

        <div className="max-w-md mx-auto">
          <div className="h-14 w-14 rounded-2xl bg-blue-50 text-blue-600 mx-auto flex items-center justify-center mb-3">
            {isUploading ? (
              <div className="animate-spin rounded-full h-7 w-7 border-b-2 border-blue-600" />
            ) : (
              <Upload className="h-7 w-7" />
            )}
          </div>

          <h3 className="font-bold text-slate-800 text-base">
            {isUploading ? "Ingesting & Parsing Document..." : "Upload Research Document"}
          </h3>

          <p className="text-xs text-slate-500 mt-1">
            Drag & drop your PDF, DOCX, TXT, Markdown, or LaTeX paper here, or click to browse.
          </p>

          <div className="flex items-center justify-center gap-2 mt-4 text-[10px] uppercase font-bold tracking-wider text-slate-400">
            <span className="px-2 py-0.5 bg-slate-100 rounded border border-slate-200">PDF</span>
            <span className="px-2 py-0.5 bg-slate-100 rounded border border-slate-200">DOCX</span>
            <span className="px-2 py-0.5 bg-slate-100 rounded border border-slate-200">TXT</span>
            <span className="px-2 py-0.5 bg-slate-100 rounded border border-slate-200">MD</span>
            <span className="px-2 py-0.5 bg-slate-100 rounded border border-slate-200">TEX</span>
          </div>

          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="mt-5 inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-md shadow-blue-600/20 disabled:opacity-50"
          >
            <Upload className="h-3.5 w-3.5" /> Select File from Computer
          </button>

          {uploadError && (
            <p className="mt-3 text-xs font-semibold text-rose-600 bg-rose-50 p-2 rounded border border-rose-200">
              {uploadError}
            </p>
          )}
        </div>
      </div>

      {/* Document List Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50/50 flex items-center justify-between">
          <h3 className="font-bold text-slate-800 text-base">Project Research Documents</h3>
          <span className="text-xs font-semibold text-slate-500">
            {documents?.length ?? 0} Documents
          </span>
        </div>

        {documentsLoading ? (
          <div className="p-8 text-center text-slate-400 text-sm">Loading documents...</div>
        ) : !documents || documents.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="h-10 w-10 text-slate-300 mx-auto mb-2" />
            <p className="font-semibold text-slate-600 text-sm">No documents in this project yet</p>
            <p className="text-xs text-slate-400 mt-1">Upload a research file above to trigger canonical extraction and NLP analysis.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {documents.map((doc: any) => (
              <div key={doc.id} className="p-5 hover:bg-slate-50/80 transition-colors flex items-center justify-between">
                <div className="flex items-start gap-4">
                  <div className="h-10 w-10 rounded-xl bg-slate-100 text-slate-600 flex items-center justify-center font-bold text-xs uppercase shrink-0 mt-0.5">
                    {doc.file_type}
                  </div>
                  <div>
                    <Link
                      href={`/documents/${doc.id}`}
                      className="font-bold text-slate-900 hover:text-blue-600 text-base transition-colors"
                    >
                      {doc.title}
                    </Link>
                    <p className="text-xs text-slate-500 mt-0.5">Original File: {doc.original_filename}</p>

                    <div className="flex items-center gap-3 mt-2 text-[11px]">
                      <span className="inline-flex items-center gap-1 font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                        <CheckCircle2 className="h-3 w-3 text-emerald-600" /> CDM Version {doc.latest_version_number ?? 1}
                      </span>
                      <span className="text-slate-400 font-mono text-[10px]">
                        SHA-256: {doc.sha256_hash?.substring(0, 12)}...
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Link
                    href={`/documents/${doc.id}`}
                    className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center gap-1.5 shadow-sm transition-all"
                  >
                    Open Workspace <ArrowRight className="h-3.5 w-3.5" />
                  </Link>

                  <button
                    onClick={() => {
                      if (confirm("Delete this document and all its CDM versions?")) {
                        deleteDocumentMutation.mutate(doc.id);
                      }
                    }}
                    className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                    title="Delete document"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
