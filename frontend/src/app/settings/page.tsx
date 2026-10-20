"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import {
  Settings as SettingsIcon,
  User as UserIcon,
  Sparkles,
  BookOpen,
  Sliders,
  Save,
  CheckCircle,
  Key,
  ShieldAlert,
  Building,
  GraduationCap
} from "lucide-react";

export default function SettingsPage() {
  const { user } = useAuth();

  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("RESEARCHER");
  const [affiliation, setAffiliation] = useState("");
  const [researchDomain, setResearchDomain] = useState("Computer Science");

  // AI Intelligence Settings
  const [geminiApiKey, setGeminiApiKey] = useState("");
  const [selectedModel, setSelectedModel] = useState("gemini-1.5-flash");
  const [aiTemperature, setAiTemperature] = useState("0.7");

  // Publishing Defaults
  const [defaultPublisher, setDefaultPublisher] = useState("IEEE");
  const [defaultExportFormat, setDefaultExportFormat] = useState("PDF");
  const [defaultCitationStyle, setDefaultCitationStyle] = useState("Numeric [1]");

  // Editor Preferences
  const [strictValidation, setStrictValidation] = useState(true);
  const [autoDraftOutline, setAutoDraftOutline] = useState(true);

  const [isSaving, setIsSaving] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || "");
      setRole(user.role || "RESEARCHER");

      const prefs = (user as any).preferences || {};
      setAffiliation(prefs.affiliation || "");
      setResearchDomain(prefs.research_domain || "Computer Science");
      setGeminiApiKey(prefs.gemini_api_key || "");
      setSelectedModel(prefs.ai_model || "gemini-1.5-flash");
      setAiTemperature(prefs.ai_temperature || "0.7");
      setDefaultPublisher(prefs.default_publisher || "IEEE");
      setDefaultExportFormat(prefs.default_export_format || "PDF");
      setDefaultCitationStyle(prefs.default_citation_style || "Numeric [1]");
      if (prefs.strict_validation !== undefined) setStrictValidation(prefs.strict_validation);
      if (prefs.auto_draft_outline !== undefined) setAutoDraftOutline(prefs.auto_draft_outline);
    }
  }, [user]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setStatusMessage(null);

    try {
      const preferences = {
        affiliation,
        research_domain: researchDomain,
        gemini_api_key: geminiApiKey,
        ai_model: selectedModel,
        ai_temperature: aiTemperature,
        default_publisher: defaultPublisher,
        default_export_format: defaultExportFormat,
        default_citation_style: defaultCitationStyle,
        strict_validation: strictValidation,
        auto_draft_outline: autoDraftOutline
      };

      const res = await api.put("/auth/profile", {
        full_name: fullName,
        role: role,
        preferences: preferences
      });

      if (res.data.success) {
        setStatusMessage({ type: "success", text: "Settings and preferences saved successfully!" });
      }
    } catch (err: any) {
      setStatusMessage({
        type: "error",
        text: err.response?.data?.detail || "Failed to save settings. Please try again."
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <SettingsIcon className="h-6 w-6 text-blue-600" />
            Platform & Research Settings
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Manage your personal profile, Google Gemini AI configuration, and academic publishing preferences.
          </p>
        </div>

        <button
          onClick={handleSave}
          disabled={isSaving}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-md shadow-blue-500/20 disabled:opacity-50 transition-colors"
        >
          <Save className="h-4 w-4" />
          {isSaving ? "Saving..." : "Save Changes"}
        </button>
      </div>

      {statusMessage && (
        <div
          className={`p-4 rounded-xl border text-sm flex items-center gap-2.5 ${
            statusMessage.type === "success"
              ? "bg-emerald-50 text-emerald-800 border-emerald-200"
              : "bg-rose-50 text-rose-800 border-rose-200"
          }`}
        >
          {statusMessage.type === "success" ? (
            <CheckCircle className="h-4 w-4 text-emerald-600 shrink-0" />
          ) : (
            <ShieldAlert className="h-4 w-4 text-rose-600 shrink-0" />
          )}
          {statusMessage.text}
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* 1. Profile Information */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-5">
          <div className="flex items-center gap-2.5 pb-4 border-b border-slate-100">
            <UserIcon className="h-5 w-5 text-indigo-600" />
            <div>
              <h2 className="text-base font-bold text-slate-900">Researcher Profile</h2>
              <p className="text-xs text-slate-500">Your identification across research projects and publications</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Dr. Jane Doe"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Account Email</label>
              <input
                type="email"
                value={user?.email || ""}
                disabled
                className="w-full px-3.5 py-2 rounded-lg border border-slate-200 bg-slate-50 text-slate-500 text-sm cursor-not-allowed"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Academic / Research Role</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="RESEARCHER">Primary Researcher</option>
                <option value="REVIEWER">Peer Reviewer / Editor</option>
                <option value="PUBLISHER">Publisher Delegate</option>
                <option value="ADMIN">Administrator</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Institution / Affiliation</label>
              <input
                type="text"
                value={affiliation}
                onChange={(e) => setAffiliation(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Stanford University / MIT CSAIL"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 mb-1">Primary Research Domain</label>
              <select
                value={researchDomain}
                onChange={(e) => setResearchDomain(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Computer Science">Computer Science & Artificial Intelligence</option>
                <option value="Physics">Physics & Applied Mathematics</option>
                <option value="Medicine">Medicine & Biomedical Sciences</option>
                <option value="Engineering">Electrical & Mechanical Engineering</option>
                <option value="Economics">Economics & Quantitative Finance</option>
                <option value="Multidisciplinary">Multidisciplinary Sciences</option>
              </select>
            </div>
          </div>
        </div>

        {/* 2. Google Gemini & AI Assistant Settings */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-5">
          <div className="flex items-center gap-2.5 pb-4 border-b border-slate-100">
            <Sparkles className="h-5 w-5 text-amber-500" />
            <div>
              <h2 className="text-base font-bold text-slate-900">AI Intelligence & Google Gemini API</h2>
              <p className="text-xs text-slate-500">Configure your LLM reasoning engine, custom API key, and model parameters</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center justify-between">
                <span>Google Gemini API Key (Optional Override)</span>
                <span className="text-[11px] text-slate-400 font-normal">Leave blank to use platform environment default</span>
              </label>
              <div className="relative">
                <input
                  type="password"
                  value={geminiApiKey}
                  onChange={(e) => setGeminiApiKey(e.target.value)}
                  className="w-full pl-9 pr-3.5 py-2 rounded-lg border border-slate-300 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="AIzaSy..."
                />
                <Key className="h-4 w-4 text-slate-400 absolute left-3 top-2.5" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Gemini Model Tier</label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="gemini-1.5-flash">Gemini 1.5 Flash (Ultra-fast latency, high throughput)</option>
                <option value="gemini-1.5-pro">Gemini 1.5 Pro (Deep complex academic reasoning)</option>
                <option value="gemini-2.0-flash">Gemini 2.0 Flash (Next-gen reasoning & speed)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center justify-between">
                <span>Generation Temperature</span>
                <span className="font-mono text-slate-500">{aiTemperature}</span>
              </label>
              <input
                type="range"
                min="0.0"
                max="1.0"
                step="0.1"
                value={aiTemperature}
                onChange={(e) => setAiTemperature(e.target.value)}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600 mt-2"
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                <span>0.0 (Precise / Academic)</span>
                <span>1.0 (Creative / Exploratory)</span>
              </div>
            </div>
          </div>
        </div>

        {/* 3. Publishing & Formatting Defaults */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-5">
          <div className="flex items-center gap-2.5 pb-4 border-b border-slate-100">
            <BookOpen className="h-5 w-5 text-emerald-600" />
            <div>
              <h2 className="text-base font-bold text-slate-900">Publishing Defaults</h2>
              <p className="text-xs text-slate-500">Default target publisher, bibliography styles, and export formats</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Default Publisher</label>
              <select
                value={defaultPublisher}
                onChange={(e) => setDefaultPublisher(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="IEEE">IEEE (Institute of Electrical and Electronics Engineers)</option>
                <option value="ACM">ACM (Association for Computing Machinery)</option>
                <option value="ELSEVIER">Elsevier Science</option>
                <option value="SPRINGER">Springer Nature LNCS</option>
                <option value="NATURE">Nature Publishing Group</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Default Export Format</label>
              <select
                value={defaultExportFormat}
                onChange={(e) => setDefaultExportFormat(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="PDF">PDF (Publisher Ready Print)</option>
                <option value="DOCX">Microsoft Word (.docx)</option>
                <option value="LATEX">LaTeX Source (.tex bundle)</option>
                <option value="HTML">Academic Responsive HTML</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Default Citation Style</label>
              <select
                value={defaultCitationStyle}
                onChange={(e) => setDefaultCitationStyle(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Numeric [1]">Numeric [1] (IEEE, ACM, Springer)</option>
                <option value="Author-Year (APA)">Author-Year (APA, Elsevier)</option>
                <option value="Numbered superscripts">Numbered superscripts (Nature)</option>
                <option value="Harvard">Harvard Reference Format</option>
              </select>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 space-y-3">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={strictValidation}
                onChange={(e) => setStrictValidation(e.target.checked)}
                className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <span className="text-xs font-semibold text-slate-800">Strict Citation Cross-Referencing</span>
                <p className="text-[11px] text-slate-500">Flag orphan references and uncited bibliography items with high severity warnings</p>
              </div>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={autoDraftOutline}
                onChange={(e) => setAutoDraftOutline(e.target.checked)}
                className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <span className="text-xs font-semibold text-slate-800">Enable 1-Click AI Section Outlining</span>
                <p className="text-[11px] text-slate-500">Provide quick prompt actions directly inside validation deficiency cards</p>
              </div>
            </label>
          </div>
        </div>

        {/* Footer Save Action */}
        <div className="flex justify-end gap-3 pt-4">
          <button
            type="submit"
            disabled={isSaving}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-md shadow-blue-500/20 disabled:opacity-50 transition-colors"
          >
            <Save className="h-4 w-4" />
            {isSaving ? "Saving Settings..." : "Save Settings"}
          </button>
        </div>
      </form>
    </div>
  );
}
