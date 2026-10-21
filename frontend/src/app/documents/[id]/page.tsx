"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import {
  FileText,
  Edit3,
  BrainCircuit,
  ShieldCheck,
  Sparkles,
  Download,
  Save,
  Plus,
  Trash2,
  CheckCircle,
  AlertTriangle,
  Info,
  ArrowLeft,
  RefreshCw,
  ExternalLink,
  Layers,
  Check,
  Clock,
  RotateCcw,
  BookMarked,
  Table as TableIcon,
  Image as ImageIcon,
  X,
  MessageSquare,
  Bot,
  Wand2
} from "lucide-react";

export default function DocumentWorkspacePage() {
  const { id: documentId } = useParams();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<"cdm" | "nlp" | "validation" | "ai" | "export">("cdm");

  // State for CDM Editor
  const [cdmState, setCdmState] = useState<any>(null);
  const [commitMessage, setCommitMessage] = useState("Updated via CDM Editor");
  const [selectedPublisher, setSelectedPublisher] = useState("IEEE");
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isTransformingIEEE, setIsTransformingIEEE] = useState(false);

  // State for AI Assistant
  const [aiAction, setAiAction] = useState("improve_wording");
  const [aiSelectedText, setAiSelectedText] = useState("");
  const [aiPrompt, setAiPrompt] = useState("");
  const [aiResponse, setAiResponse] = useState<any>(null);

  // State for Generation
  const [exportFormat, setExportFormat] = useState("PDF");
  const [lastGeneratedExport, setLastGeneratedExport] = useState<any>(null);

  // Fetch document metadata
  const { data: document, isLoading: docLoading } = useQuery({
    queryKey: ["document", documentId],
    queryFn: async () => {
      const res = await api.get(`/documents/${documentId}`);
      return res.data.data;
    },
  });

  // Fetch latest CDM
  const { data: cdmVersion, isLoading: cdmLoading } = useQuery({
    queryKey: ["cdm", documentId],
    queryFn: async () => {
      const res = await api.get(`/cdm/${documentId}`);
      const data = res.data.data;
      if (!cdmState) {
        setCdmState(data.cdm_data);
      }
      return data;
    },
  });

  // Fetch versions history
  const { data: versionsList } = useQuery({
    queryKey: ["versions", documentId],
    queryFn: async () => {
      const res = await api.get(`/cdm/${documentId}/versions`);
      return res.data.data;
    },
  });

  // Fetch AI conversation history
  const { data: conversationData } = useQuery({
    queryKey: ["ai_conversation", documentId],
    queryFn: async () => {
      const res = await api.get(`/ai/conversation/${documentId}`);
      return res.data.data;
    },
  });

  // Fetch Analysis
  const { data: analysisData } = useQuery({
    queryKey: ["analysis", documentId],
    queryFn: async () => {
      const res = await api.get(`/analysis/${documentId}`);
      return res.data.data;
    },
  });

  // Fetch Validation
  const { data: validationData } = useQuery({
    queryKey: ["validation", documentId, selectedPublisher],
    queryFn: async () => {
      const res = await api.get(`/validation/${documentId}?publisher_code=${selectedPublisher}`);
      return res.data.data;
    },
  });

  // Save CDM Mutation
  const saveCdmMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await api.post(`/cdm/${documentId}/update`, payload);
      return res.data.data;
    },
    onSuccess: (data) => {
      setCdmState(data.cdm_data);
      queryClient.invalidateQueries({ queryKey: ["cdm", documentId] });
      queryClient.invalidateQueries({ queryKey: ["versions", documentId] });
      queryClient.invalidateQueries({ queryKey: ["analysis", documentId] });
      queryClient.invalidateQueries({ queryKey: ["validation", documentId] });
      alert(`Saved CDM Version ${data.version_number} successfully!`);
    },
  });

  // Rollback Mutation
  const rollbackMutation = useMutation({
    mutationFn: async (targetVer: number) => {
      const res = await api.post(`/cdm/${documentId}/rollback/${targetVer}`);
      return res.data.data;
    },
    onSuccess: (data) => {
      setCdmState(data.cdm_data);
      queryClient.invalidateQueries({ queryKey: ["cdm", documentId] });
      queryClient.invalidateQueries({ queryKey: ["versions", documentId] });
      queryClient.invalidateQueries({ queryKey: ["analysis", documentId] });
      queryClient.invalidateQueries({ queryKey: ["validation", documentId] });
      setIsHistoryOpen(false);
      alert(`Restored document to Version ${data.version_number}!`);
    },
  });

  // AI Assistant Mutation
  const aiMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await api.post(`/ai/assistant/${documentId}`, payload);
      return res.data.data;
    },
    onSuccess: (data) => {
      setAiResponse(data);
      queryClient.invalidateQueries({ queryKey: ["ai_conversation", documentId] });
    },
  });

  // Clear AI Conversation Mutation
  const clearAiMutation = useMutation({
    mutationFn: async () => {
      await api.delete(`/ai/conversation/${documentId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai_conversation", documentId] });
      setAiResponse(null);
    },
  });

  // Export Generation Mutation
  const exportMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await api.post(`/generation/generate/${documentId}`, payload);
      return res.data.data;
    },
    onSuccess: (data) => {
      setLastGeneratedExport(data);
      queryClient.invalidateQueries({ queryKey: ["exports"] });
    },
  });

  const getFileExtension = (format: string) => {
    switch (format?.toUpperCase()) {
      case "PDF": return ".pdf";
      case "DOCX": return ".docx";
      case "LATEX": return ".tex";
      case "HTML": return ".html";
      default: return ".bin";
    }
  };

  const handleDownloadArtifact = (exportId: string, format: string) => {
    const ext = getFileExtension(format);
    api.get(`/exports/${exportId}/download`, {
      responseType: "blob",
    })
      .then((res) => {
        const url = window.URL.createObjectURL(new Blob([res.data]));
        const a = document.createElement("a");
        a.href = url;
        a.download = `morphe_export_${exportId.substring(0, 8)}${ext}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      })
      .catch((err) => alert("Failed to download artifact: " + (err.response?.data?.detail || err.message)));
  };

  if (docLoading || cdmLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center space-y-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto" />
          <p className="text-sm font-semibold text-slate-600">Loading Document Intelligence Workspace...</p>
        </div>
      </div>
    );
  }

  const cdm = cdmState || cdmVersion?.cdm_data;
  const nlp = analysisData?.nlp_analysis;
  const domain = analysisData?.domain_analysis;
  const validation = validationData?.validation;

  const handleSaveCDM = () => {
    saveCdmMutation.mutate({
      cdm_data: cdm,
      commit_message: commitMessage
    });
  };

  const handleRunAI = () => {
    aiMutation.mutate({
      action: aiAction,
      selected_text: aiSelectedText,
      prompt: aiPrompt,
      publisher_code: selectedPublisher
    });
  };

  const handleApplyAItoAbstract = (text: string) => {
    const cleaned = text.replace(/^(Generated Abstract:\s*|Enhanced Academic Wording:\s*|Summary of '[^']+':\s*)/i, "").trim();
    setCdmState({
      ...cdm,
      metadata: { ...cdm.metadata, abstract: cleaned }
    });
    alert("Applied AI generated text into Document Abstract! Click 'Save CDM Version' to commit.");
  };

  const handleAutoDraftSection = (secName: string) => {
    setActiveTab("ai");
    setAiAction("suggest_structure");
    setAiPrompt(`Draft a standard research outline and academic paragraphs for missing section: ${secName}`);
  };

  const handleTransformToIEEE = async () => {
    setIsTransformingIEEE(true);
    try {
      const res = await api.post(`/cdm/${documentId}/transform/ieee`);
      if (res.data.success) {
        setCdmState(res.data.data.cdm_data);
        queryClient.invalidateQueries({ queryKey: ["cdm", documentId] });
        queryClient.invalidateQueries({ queryKey: ["validation", documentId] });
        queryClient.invalidateQueries({ queryKey: ["versions", documentId] });
        setSelectedPublisher("IEEE");
        setActiveTab("validation");
        alert("Paper successfully transformed into standard IEEE format with Roman numeral sections and Index Terms!");
      }
    } catch (err: any) {
      alert("Failed to transform to IEEE: " + (err.response?.data?.detail || err.message));
    } finally {
      setIsTransformingIEEE(false);
    }
  };

  const handleDownloadOriginal = () => {
    api.get(`/documents/${documentId}/download-original`, {
      responseType: "blob",
    })
      .then((res) => {
        const url = window.URL.createObjectURL(new Blob([res.data]));
        const a = document.createElement("a");
        a.href = url;
        a.download = document?.original_filename || `original_document.${document?.file_type || "bin"}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      })
      .catch((err) => alert("Failed to download original document: " + (err.response?.data?.detail || err.message)));
  };

  const handleGenerateExport = () => {
    exportMutation.mutate({
      format: exportFormat,
      publisher_code: selectedPublisher
    });
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header Navigation */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <Link
            href={`/projects/${document?.project_id}`}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 mb-1"
          >
            <ArrowLeft className="h-3.5 w-3.5" /> Back to Project
          </Link>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            {document?.title}
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 border border-blue-200">
              CDM v{cdmVersion?.version_number ?? 1}
            </span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            File: <strong>{document?.original_filename}</strong> ({document?.file_type?.toUpperCase()})
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleTransformToIEEE}
            disabled={isTransformingIEEE}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-gradient-to-r from-blue-700 via-indigo-600 to-blue-800 hover:from-blue-600 hover:to-indigo-500 text-white font-semibold text-xs shadow-md shadow-blue-700/20 disabled:opacity-50 transition-all border border-blue-500/30"
            title="Auto-restructure and format this paper into standard IEEE conference/journal layout"
          >
            <Sparkles className="h-3.5 w-3.5 text-amber-300" />
            {isTransformingIEEE ? "Structuring..." : "Format as IEEE"}
          </button>

          <button
            onClick={handleDownloadOriginal}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white hover:bg-slate-50 text-slate-700 font-semibold text-xs border border-slate-300 shadow-sm transition-colors"
            title="Download Original Uploaded File"
          >
            <Download className="h-3.5 w-3.5 text-blue-600" />
            Download Original
          </button>

          <button
            onClick={() => setIsHistoryOpen(true)}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs border border-slate-300 shadow-sm"
          >
            <Clock className="h-3.5 w-3.5 text-slate-600" />
            History ({versionsList?.length ?? 1} commits)
          </button>

          <button
            onClick={handleSaveCDM}
            disabled={saveCdmMutation.isPending}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-md shadow-emerald-600/20 disabled:opacity-50"
          >
            <Save className="h-4 w-4" />
            {saveCdmMutation.isPending ? "Saving..." : "Save CDM Version"}
          </button>
        </div>
      </div>

      {/* Main Workspace Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 overflow-x-auto pb-0">
        {[
          { id: "cdm", label: "CDM Editor", icon: Edit3 },
          { id: "nlp", label: "NLP & Domain Analysis", icon: BrainCircuit },
          { id: "validation", label: "Publisher & Validation", icon: ShieldCheck },
          { id: "ai", label: "AI Research Assistant", icon: Sparkles },
          { id: "export", label: "Generate & Export", icon: Download },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 font-semibold text-sm transition-all whitespace-nowrap ${
                isActive
                  ? "border-blue-600 text-blue-600 bg-blue-50/50"
                  : "border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300"
              }`}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* TAB 1: CDM EDITOR */}
      {activeTab === "cdm" && cdm && (
        <div className="space-y-6">
          {/* Metadata Block */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
            <h3 className="font-bold text-slate-900 text-base flex items-center gap-2 border-b border-slate-100 pb-3">
              <FileText className="h-4 w-4 text-blue-600" /> Document Metadata
            </h3>

            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Research Title
                </label>
                <input
                  type="text"
                  value={cdm.metadata?.title || ""}
                  onChange={(e) =>
                    setCdmState({
                      ...cdm,
                      metadata: { ...cdm.metadata, title: e.target.value },
                    })
                  }
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm font-semibold focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Abstract
                </label>
                <textarea
                  rows={4}
                  value={cdm.metadata?.abstract || ""}
                  onChange={(e) =>
                    setCdmState({
                      ...cdm,
                      metadata: { ...cdm.metadata, abstract: e.target.value },
                    })
                  }
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Keywords (comma separated)
                </label>
                <input
                  type="text"
                  value={cdm.metadata?.keywords?.join(", ") || ""}
                  onChange={(e) =>
                    setCdmState({
                      ...cdm,
                      metadata: {
                        ...cdm.metadata,
                        keywords: e.target.value.split(",").map((k) => k.trim()),
                      },
                    })
                  }
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Commit Message for next version
                </label>
                <input
                  type="text"
                  value={commitMessage}
                  onChange={(e) => setCommitMessage(e.target.value)}
                  placeholder="e.g. Updated methodology section and added bibliography"
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-xs text-slate-600 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Authors List */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-base">Authors & Affiliations</h3>
              <button
                onClick={() =>
                  setCdmState({
                    ...cdm,
                    metadata: {
                      ...cdm.metadata,
                      authors: [...(cdm.metadata.authors || []), { name: "New Author", affiliation: "University", email: "" }],
                    },
                  })
                }
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 text-blue-600 font-semibold text-xs hover:bg-blue-100"
              >
                <Plus className="h-3.5 w-3.5" /> Add Author
              </button>
            </div>

            <div className="space-y-3">
              {(cdm.metadata?.authors || []).map((author: any, idx: number) => (
                <div key={idx} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <input
                    type="text"
                    placeholder="Author Name"
                    value={author.name}
                    onChange={(e) => {
                      const newAuthors = [...cdm.metadata.authors];
                      newAuthors[idx].name = e.target.value;
                      setCdmState({ ...cdm, metadata: { ...cdm.metadata, authors: newAuthors } });
                    }}
                    className="flex-1 rounded border border-slate-300 px-3 py-1.5 text-xs font-semibold"
                  />
                  <input
                    type="text"
                    placeholder="Affiliation"
                    value={author.affiliation || ""}
                    onChange={(e) => {
                      const newAuthors = [...cdm.metadata.authors];
                      newAuthors[idx].affiliation = e.target.value;
                      setCdmState({ ...cdm, metadata: { ...cdm.metadata, authors: newAuthors } });
                    }}
                    className="flex-1 rounded border border-slate-300 px-3 py-1.5 text-xs"
                  />
                  <button
                    onClick={() => {
                      const newAuthors = cdm.metadata.authors.filter((_: any, i: number) => i !== idx);
                      setCdmState({ ...cdm, metadata: { ...cdm.metadata, authors: newAuthors } });
                    }}
                    className="text-rose-500 hover:text-rose-700 p-1"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Structured Sections */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-base">Hierarchical Sections</h3>
              <button
                onClick={() =>
                  setCdmState({
                    ...cdm,
                    sections: [
                      ...(cdm.sections || []),
                      {
                        id: `sec_${(cdm.sections?.length || 0) + 1}`,
                        title: "New Section",
                        level: 1,
                        content: "",
                        order: (cdm.sections?.length || 0) + 1,
                        subsections: []
                      }
                    ],
                  })
                }
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 text-blue-600 font-semibold text-xs hover:bg-blue-100"
              >
                <Plus className="h-3.5 w-3.5" /> Add Section
              </button>
            </div>

            <div className="space-y-4">
              {(cdm.sections || []).map((sec: any, idx: number) => (
                <div key={sec.id || idx} className="p-4 bg-slate-50/60 rounded-xl border border-slate-200 space-y-3">
                  <div className="flex items-center justify-between gap-3">
                    <input
                      type="text"
                      value={sec.title}
                      onChange={(e) => {
                        const newSecs = [...cdm.sections];
                        newSecs[idx].title = e.target.value;
                        setCdmState({ ...cdm, sections: newSecs });
                      }}
                      className="flex-1 font-bold text-slate-900 text-sm bg-white rounded border border-slate-300 px-3 py-1.5"
                    />
                    <button
                      onClick={() => {
                        const newSecs = cdm.sections.filter((_: any, i: number) => i !== idx);
                        setCdmState({ ...cdm, sections: newSecs });
                      }}
                      className="text-rose-500 hover:text-rose-700 p-1"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>

                  <textarea
                    rows={4}
                    value={sec.content}
                    onChange={(e) => {
                      const newSecs = [...cdm.sections];
                      newSecs[idx].content = e.target.value;
                      setCdmState({ ...cdm, sections: newSecs });
                    }}
                    placeholder="Section content text..."
                    className="w-full bg-white rounded border border-slate-300 px-3 py-2 text-xs text-slate-800"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* References & Citations */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
                <BookMarked className="h-4 w-4 text-blue-600" /> Bibliography & References
              </h3>
              <button
                onClick={() => {
                  const currentRefs = cdm.references || [];
                  const nextId = currentRefs.length + 1;
                  setCdmState({
                    ...cdm,
                    references: [
                      ...currentRefs,
                      {
                        id: `ref_${nextId}`,
                        key: `[${nextId}]`,
                        title: "New Reference Title",
                        text: `[${nextId}] Author, "Title", Journal, 2024.`,
                        authors: ["Author et al."],
                        year: "2024",
                        venue: "Conference/Journal",
                        doi: ""
                      }
                    ]
                  });
                }}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 text-blue-600 font-semibold text-xs hover:bg-blue-100"
              >
                <Plus className="h-3.5 w-3.5" /> Add Reference
              </button>
            </div>

            <div className="space-y-3">
              {(cdm.references || []).length === 0 ? (
                <p className="text-xs text-slate-400 italic">No references extracted yet. Click Add Reference above.</p>
              ) : (
                (cdm.references || []).map((ref: any, idx: number) => (
                  <div key={ref.id || idx} className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-blue-700 bg-blue-100 px-2 py-0.5 rounded">
                        {ref.key || `[${idx + 1}]`}
                      </span>
                      <input
                        type="text"
                        placeholder="Full Reference Text / Citation string"
                        value={ref.text || ""}
                        onChange={(e) => {
                          const newRefs = [...cdm.references];
                          newRefs[idx].text = e.target.value;
                          setCdmState({ ...cdm, references: newRefs });
                        }}
                        className="flex-1 rounded border border-slate-300 px-3 py-1 text-xs text-slate-800"
                      />
                      <button
                        onClick={() => {
                          const newRefs = cdm.references.filter((_: any, i: number) => i !== idx);
                          setCdmState({ ...cdm, references: newRefs });
                        }}
                        className="text-rose-500 hover:text-rose-700 p-1"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Tables & Figures */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Tables */}
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-3">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                <h4 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                  <TableIcon className="h-4 w-4 text-emerald-600" /> Tables ({cdm.tables?.length || 0})
                </h4>
                <button
                  onClick={() => {
                    const currentTables = cdm.tables || [];
                    const nextId = currentTables.length + 1;
                    setCdmState({
                      ...cdm,
                      tables: [
                        ...currentTables,
                        {
                          id: `tbl_${nextId}`,
                          caption: `Table ${nextId}: Experimental Results`,
                          data: [["Method", "Accuracy", "Latency"], ["Baseline", "89.2%", "45ms"], ["Proposed", "96.4%", "27ms"]]
                        }
                      ]
                    });
                  }}
                  className="text-xs text-emerald-600 font-semibold hover:underline flex items-center gap-1"
                >
                  <Plus className="h-3 w-3" /> Add Table
                </button>
              </div>

              {(cdm.tables || []).length === 0 ? (
                <p className="text-xs text-slate-400">No tables defined.</p>
              ) : (
                (cdm.tables || []).map((t: any, idx: number) => (
                  <div key={t.id || idx} className="p-3 bg-slate-50 rounded border border-slate-200 text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <input
                        type="text"
                        value={t.caption || ""}
                        onChange={(e) => {
                          const newTables = [...cdm.tables];
                          newTables[idx].caption = e.target.value;
                          setCdmState({ ...cdm, tables: newTables });
                        }}
                        className="font-semibold text-slate-900 bg-white border border-slate-300 rounded px-2 py-0.5 text-xs w-full mr-2"
                      />
                      <button
                        onClick={() => {
                          const newTables = cdm.tables.filter((_: any, i: number) => i !== idx);
                          setCdmState({ ...cdm, tables: newTables });
                        }}
                        className="text-rose-500 hover:text-rose-700"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Figures */}
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-3">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                <h4 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                  <ImageIcon className="h-4 w-4 text-purple-600" /> Figures ({cdm.figures?.length || 0})
                </h4>
                <button
                  onClick={() => {
                    const currentFigs = cdm.figures || [];
                    const nextId = currentFigs.length + 1;
                    setCdmState({
                      ...cdm,
                      figures: [
                        ...currentFigs,
                        {
                          id: `fig_${nextId}`,
                          caption: `Figure ${nextId}: Architecture Diagram`,
                          label: `fig:${nextId}`,
                          source: ""
                        }
                      ]
                    });
                  }}
                  className="text-xs text-purple-600 font-semibold hover:underline flex items-center gap-1"
                >
                  <Plus className="h-3 w-3" /> Add Figure
                </button>
              </div>

              {(cdm.figures || []).length === 0 ? (
                <p className="text-xs text-slate-400">No figures defined.</p>
              ) : (
                (cdm.figures || []).map((f: any, idx: number) => (
                  <div key={f.id || idx} className="p-3 bg-slate-50 rounded border border-slate-200 text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <input
                        type="text"
                        value={f.caption || ""}
                        onChange={(e) => {
                          const newFigs = [...cdm.figures];
                          newFigs[idx].caption = e.target.value;
                          setCdmState({ ...cdm, figures: newFigs });
                        }}
                        className="font-semibold text-slate-900 bg-white border border-slate-300 rounded px-2 py-0.5 text-xs w-full mr-2"
                      />
                      <button
                        onClick={() => {
                          const newFigs = cdm.figures.filter((_: any, i: number) => i !== idx);
                          setCdmState({ ...cdm, figures: newFigs });
                        }}
                        className="text-rose-500 hover:text-rose-700"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: NLP & DOMAIN INTELLIGENCE */}
      {activeTab === "nlp" && (
        <div className="space-y-6">
          {/* Domain Intelligence Card */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <h3 className="font-bold text-slate-900 text-base mb-4 flex items-center gap-2">
              <BrainCircuit className="h-5 w-5 text-indigo-600" /> Domain & Structural Classification
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-indigo-50/50 p-4 rounded-xl border border-indigo-100">
                <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600">Primary Domain</span>
                <h4 className="font-extrabold text-indigo-950 text-lg mt-0.5">{domain?.primary_domain || "Computer Science"}</h4>
              </div>
              <div className="bg-blue-50/50 p-4 rounded-xl border border-blue-100">
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600">Subdomain</span>
                <h4 className="font-extrabold text-blue-950 text-lg mt-0.5">{domain?.subdomain || "Machine Learning"}</h4>
              </div>
              <div className="bg-emerald-50/50 p-4 rounded-xl border border-emerald-100">
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-600">Research Type</span>
                <h4 className="font-extrabold text-emerald-950 text-lg mt-0.5">{domain?.research_type || "Experimental"}</h4>
              </div>
              <div className="bg-purple-50/50 p-4 rounded-xl border border-purple-100">
                <span className="text-[10px] font-bold uppercase tracking-wider text-purple-600">Classification Confidence</span>
                <h4 className="font-extrabold text-purple-950 text-lg mt-0.5">{Math.round((domain?.confidence || 0.95) * 100)}%</h4>
              </div>
            </div>

            {/* Evidence details */}
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
              <h4 className="font-bold text-slate-800 text-xs uppercase tracking-wider mb-2">Classification Evidence</h4>
              <div className="space-y-1.5">
                {(domain?.evidence || []).map((ev: any, idx: number) => (
                  <p key={idx} className="text-xs text-slate-600 flex items-center gap-2">
                    <CheckCircle className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
                    <strong>{ev.factor}:</strong> {ev.detail}
                  </p>
                ))}
              </div>
            </div>
          </div>

          {/* Keywords & Named Entities */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Keywords */}
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
              <h4 className="font-bold text-slate-900 text-sm mb-3">Extracted Domain Keywords</h4>
              <div className="flex flex-wrap gap-2">
                {(nlp?.keywords || []).map((kw: any, idx: number) => (
                  <span key={idx} className="px-3 py-1 rounded-full bg-slate-100 text-slate-800 font-semibold text-xs border border-slate-200 flex items-center gap-1">
                    {kw.word} <span className="text-[10px] font-bold text-blue-600">({kw.score})</span>
                  </span>
                ))}
              </div>
            </div>

            {/* Named Entities */}
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
              <h4 className="font-bold text-slate-900 text-sm mb-3">Named Entities Discovered</h4>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {(nlp?.entities || []).map((ent: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between text-xs p-2 bg-slate-50 rounded border border-slate-200">
                    <span className="font-semibold text-slate-800">{ent.text}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-blue-100 text-blue-700">
                      {ent.category}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: PUBLISHER & VALIDATION */}
      {activeTab === "validation" && (
        <div className="space-y-6">
          {/* Target Publisher Selector Header */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h3 className="font-bold text-slate-900 text-base">Target Publisher Profile</h3>
              <p className="text-xs text-slate-500 mt-0.5">Select a target publisher to evaluate structural and citation compliance.</p>
            </div>
            <select
              value={selectedPublisher}
              onChange={(e) => setSelectedPublisher(e.target.value)}
              className="bg-slate-50 border border-slate-300 font-bold text-slate-800 text-sm rounded-xl px-4 py-2.5 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            >
              <option value="IEEE">IEEE Transactions Format</option>
              <option value="ACM">ACM SIGGRAPH / Conference</option>
              <option value="ELSEVIER">Elsevier Science Direct</option>
              <option value="SPRINGER">Springer Nature LNCS</option>
              <option value="NATURE">Nature Main Journal</option>
            </select>
          </div>

          {/* Validation Score Overview */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Publisher Compliance Score</span>
              <h2 className="text-3xl font-extrabold text-slate-900 mt-1">
                {validation?.overall_score ?? 94.0}%
              </h2>
              <p className="text-xs text-emerald-600 font-medium mt-1 flex items-center gap-1">
                <CheckCircle className="h-3.5 w-3.5" /> High readiness for {selectedPublisher} submission
              </p>
            </div>
            <div className="h-16 w-16 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center font-black text-xl border-4 border-emerald-500/20">
              {Math.round(validation?.overall_score ?? 94)}
            </div>
          </div>

          {/* Structural & Issues Lists */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-3">
              <h4 className="font-bold text-slate-900 text-sm border-b border-slate-100 pb-2">
                Structural Issues & Validation Output
              </h4>
              {validation?.structural_issues?.length === 0 ? (
                <p className="text-xs text-emerald-600 font-semibold flex items-center gap-1.5 p-3 bg-emerald-50 rounded-lg">
                  <CheckCircle className="h-4 w-4" /> No structural issues detected.
                </p>
              ) : (
                (validation?.structural_issues || []).map((issue: any, idx: number) => (
                  <div key={idx} className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs space-y-1">
                    <div className="flex items-center justify-between font-bold text-amber-900">
                      <span>{issue.message}</span>
                      <span className="uppercase text-[9px] px-1.5 py-0.5 rounded bg-amber-200 text-amber-800">{issue.severity}</span>
                    </div>
                    <p className="text-amber-800">Location: {issue.location}</p>
                    <p className="text-amber-700 italic">Suggestion: {issue.suggestion}</p>
                    <button
                      onClick={() => handleAutoDraftSection(issue.location)}
                      className="mt-1 inline-flex items-center gap-1 text-[11px] font-bold text-blue-600 hover:text-blue-800"
                    >
                      <Wand2 className="h-3 w-3" /> Auto-Draft with AI
                    </button>
                  </div>
                ))
              )}

              {/* Citation cross-referencing consistency issues */}
              {(validation?.citation_issues || []).length > 0 && (
                <div className="pt-2 border-t border-slate-100 space-y-2">
                  <h5 className="font-bold text-slate-800 text-xs flex items-center gap-1.5">
                    <BookMarked className="h-3.5 w-3.5 text-blue-600" /> Citation & Bibliography Consistency
                  </h5>
                  {(validation?.citation_issues || []).map((cIssue: any, idx: number) => (
                    <div key={idx} className="p-2.5 bg-blue-50/60 border border-blue-200 rounded text-xs space-y-0.5">
                      <div className="flex items-center justify-between font-semibold text-blue-900">
                        <span>{cIssue.message}</span>
                        <span className="uppercase text-[9px] px-1 rounded bg-blue-200 text-blue-800">{cIssue.severity}</span>
                      </div>
                      <p className="text-blue-700 text-[11px]">{cIssue.suggestion}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-3">
              <h4 className="font-bold text-slate-900 text-sm border-b border-slate-100 pb-2">
                {selectedPublisher} Compliance Checklist
              </h4>
              <div className="space-y-2">
                {(validation?.publisher_compliance?.checklist || []).map((chk: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs">
                    <div>
                      <p className="font-semibold text-slate-900">{chk.criterion}</p>
                      <p className="text-[11px] text-slate-500">{chk.detail}</p>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      chk.status === "PASS" ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-700"
                    }`}>
                      {chk.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: AI RESEARCH ASSISTANT */}
      {activeTab === "ai" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
            <h3 className="font-bold text-slate-900 text-base flex items-center gap-2 border-b border-slate-100 pb-3">
              <Sparkles className="h-5 w-5 text-blue-600" /> AI Assistant Actions
            </h3>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">Select Action</label>
              <select
                value={aiAction}
                onChange={(e) => setAiAction(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm font-semibold text-slate-800"
              >
                <option value="improve_wording">Improve Academic Writing Wording</option>
                <option value="explain">Explain Section / Concept</option>
                <option value="summarize">Summarize Document</option>
                <option value="suggest_structure">Suggest Section Structure</option>
                <option value="generate_abstract">Generate Abstract</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">Target / Selected Text</label>
              <textarea
                rows={4}
                value={aiSelectedText}
                onChange={(e) => setAiSelectedText(e.target.value)}
                placeholder="Paste text from document to rewrite or explain..."
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-xs text-slate-800"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">Custom Instructions (Optional)</label>
              <input
                type="text"
                value={aiPrompt}
                onChange={(e) => setAiPrompt(e.target.value)}
                placeholder="e.g. Focus on formal IEEE tone and active voice..."
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-xs text-slate-800"
              />
            </div>

            <button
              onClick={handleRunAI}
              disabled={aiMutation.isPending}
              className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-md shadow-blue-600/20 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Sparkles className="h-4 w-4" />
              {aiMutation.isPending ? "Processing AI Analysis..." : "Execute AI Assistant Action"}
            </button>
          </div>

          {/* AI Response Output & History */}
          <div className="bg-slate-900 text-slate-100 rounded-xl border border-slate-800 p-6 shadow-xl space-y-4 flex flex-col justify-between max-h-[650px] overflow-hidden">
            <div className="flex-1 flex flex-col overflow-hidden">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4 shrink-0">
                <span className="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center gap-1.5">
                  <Bot className="h-4 w-4" /> Academic Assistant & History
                </span>
                {(conversationData?.messages?.length || 0) > 0 && (
                  <button
                    onClick={() => {
                      if (confirm("Clear conversation history for this document?")) {
                        clearAiMutation.mutate();
                      }
                    }}
                    className="text-[10px] text-slate-400 hover:text-rose-400 flex items-center gap-1"
                  >
                    <Trash2 className="h-3 w-3" /> Clear History
                  </button>
                )}
              </div>

              <div className="overflow-y-auto space-y-4 pr-1 flex-1">
                {(conversationData?.messages || []).length === 0 && !aiResponse && (
                  <div className="text-center py-16 text-slate-500 text-xs">
                    Run an AI action on the left panel to preview enhanced academic wording, generated abstracts, or section explanations.
                  </div>
                )}

                {(conversationData?.messages || []).map((msg: any, idx: number) => (
                  <div key={idx} className="space-y-1.5">
                    {msg.role === "user" ? (
                      <div className="p-3 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs space-y-1">
                        <span className="text-[10px] uppercase font-bold text-blue-400">Action: {msg.action}</span>
                        {msg.selected_text && <p className="text-slate-300 italic">"{msg.selected_text}"</p>}
                        {msg.prompt && <p className="text-slate-400">Note: {msg.prompt}</p>}
                      </div>
                    ) : (
                      <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-bold text-emerald-400 uppercase">AI Recommendation</span>
                          <span className="text-[10px] text-slate-500">{new Date(msg.created_at).toLocaleTimeString()}</span>
                        </div>
                        <div className="font-mono text-slate-200 whitespace-pre-wrap">{msg.result}</div>
                        {msg.action === "generate_abstract" && (
                          <button
                            onClick={() => handleApplyAItoAbstract(msg.result)}
                            className="px-2.5 py-1 rounded bg-emerald-600/80 hover:bg-emerald-500 text-white font-semibold text-[11px] flex items-center gap-1"
                          >
                            <Check className="h-3 w-3" /> Apply to Abstract
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: GENERATE & EXPORT */}
      {activeTab === "export" && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-6 max-w-2xl">
            <h3 className="font-bold text-slate-900 text-base border-b border-slate-100 pb-3 flex items-center gap-2">
              <Download className="h-5 w-5 text-blue-600" /> Export Document Artifact
            </h3>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">Target Export Format</label>
              <div className="grid grid-cols-4 gap-3">
                {["PDF", "DOCX", "LATEX", "HTML"].map((fmt) => (
                  <button
                    key={fmt}
                    onClick={() => setExportFormat(fmt)}
                    className={`py-3 px-4 rounded-xl border font-bold text-xs transition-all ${
                      exportFormat === fmt
                        ? "bg-blue-600 text-white border-blue-600 shadow-md shadow-blue-600/20"
                        : "bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100"
                    }`}
                  >
                    {fmt}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">Publisher Profile</label>
              <select
                value={selectedPublisher}
                onChange={(e) => setSelectedPublisher(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 font-bold text-slate-800 text-sm rounded-xl px-4 py-2.5"
              >
                <option value="IEEE">IEEE Format</option>
                <option value="ACM">ACM Format</option>
                <option value="ELSEVIER">Elsevier Format</option>
                <option value="SPRINGER">Springer Nature Format</option>
                <option value="NATURE">Nature Journal Format</option>
              </select>
            </div>

            <button
              onClick={handleGenerateExport}
              disabled={exportMutation.isPending}
              className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm shadow-lg shadow-blue-600/25 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Download className="h-4 w-4" />
              {exportMutation.isPending ? "Generating Export File..." : `Generate ${exportFormat} Output`}
            </button>

            {lastGeneratedExport && (
              <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center justify-between">
                <div>
                  <h4 className="font-bold text-emerald-950 text-sm">
                    {lastGeneratedExport.format} Document Generated!
                  </h4>
                  <p className="text-xs text-emerald-700">
                    Publisher: {lastGeneratedExport.publisher_code || "IEEE"} | Size: {Math.round(lastGeneratedExport.file_size / 1024)} KB
                  </p>
                </div>
                <button
                  onClick={() => handleDownloadArtifact(lastGeneratedExport.id, lastGeneratedExport.format)}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center gap-1.5 shadow-sm"
                >
                  <Download className="h-4 w-4" /> Download File Now
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* VERSION HISTORY MODAL */}
      {isHistoryOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-4 max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
                  <Clock className="h-4 w-4 text-blue-600" /> CDM Version Commit History
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">Browse all revisions or rollback to a previous state.</p>
              </div>
              <button
                onClick={() => setIsHistoryOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="overflow-y-auto space-y-3 flex-1">
              {(versionsList || []).map((ver: any) => {
                const isCurrent = ver.version_number === cdmVersion?.version_number;
                return (
                  <div
                    key={ver.id}
                    className={`p-4 rounded-xl border flex items-center justify-between transition-all ${
                      isCurrent
                        ? "bg-blue-50/60 border-blue-300 ring-1 ring-blue-300"
                        : "bg-slate-50 border-slate-200 hover:bg-slate-100"
                    }`}
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-extrabold text-xs px-2 py-0.5 rounded bg-blue-600 text-white">
                          v{ver.version_number}
                        </span>
                        <h4 className="font-bold text-slate-900 text-sm">{ver.commit_message || "Revision Commit"}</h4>
                        {isCurrent && (
                          <span className="text-[10px] font-bold text-blue-700 bg-blue-100 px-2 py-0.5 rounded-full">
                            Active
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-400 mt-1">
                        Committed: {new Date(ver.created_at).toLocaleString()}
                      </p>
                    </div>

                    {!isCurrent && (
                      <button
                        onClick={() => {
                          if (confirm(`Rollback to Version ${ver.version_number}? Current changes will be committed as a new version.`)) {
                            rollbackMutation.mutate(ver.version_number);
                          }
                        }}
                        disabled={rollbackMutation.isPending}
                        className="px-3 py-1.5 rounded-lg bg-white border border-slate-300 text-slate-700 hover:bg-slate-100 font-semibold text-xs flex items-center gap-1 shadow-sm"
                      >
                        <RotateCcw className="h-3.5 w-3.5 text-blue-600" /> Restore
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
