"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { BookOpen, CheckCircle, Award, Layers } from "lucide-react";

export default function KnowledgeBasePage() {
  const { data: publishers, isLoading: pubLoading } = useQuery({
    queryKey: ["publishers"],
    queryFn: async () => {
      const res = await api.get("/knowledge/publishers");
      return res.data.data;
    },
  });

  const { data: citationStyles, isLoading: citeLoading } = useQuery({
    queryKey: ["citationStyles"],
    queryFn: async () => {
      const res = await api.get("/knowledge/citation-styles");
      return res.data.data;
    },
  });

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Publisher Knowledge Base</h1>
        <p className="text-sm text-slate-500 mt-1">
          Stored profiles for academic publishers, target journal guidelines, required section structures, and citation formats.
        </p>
      </div>

      {/* Publishers */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
          <BookOpen className="h-5 w-5 text-blue-600" /> Academic Publishers & Journal Profiles
        </h2>

        {pubLoading ? (
          <div className="p-8 text-center text-slate-400">Loading publishers...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {(publishers || []).map((pub: any) => (
              <div key={pub.code} className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold px-2.5 py-1 rounded bg-blue-100 text-blue-700 border border-blue-200">
                    {pub.code}
                  </span>
                  <span className="text-xs text-slate-400 font-semibold">{pub.journals?.length || 0} Listed Journals</span>
                </div>

                <div>
                  <h3 className="font-bold text-slate-900 text-base">{pub.name}</h3>
                  <p className="text-xs text-slate-500 mt-1">{pub.description}</p>
                </div>

                <div className="space-y-2 pt-2 border-t border-slate-100">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">Target Journals</h4>
                  {(pub.journals || []).map((j: any) => (
                    <div key={j.code} className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs space-y-1">
                      <div className="flex items-center justify-between font-bold text-slate-900">
                        <span>{j.name}</span>
                        <span className="text-blue-600 font-mono text-[10px]">{j.citation_style}</span>
                      </div>
                      <p className="text-slate-500 text-[11px]">
                        Required Sections: {j.required_sections?.join(", ")}
                      </p>
                      <p className="text-slate-400 text-[10px]">
                        Max Words: {j.max_words || "Unlimited"} | Abstract Limit: {j.abstract_max_words || 250} words
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Citation Styles */}
      <div className="space-y-4 pt-4 border-t border-slate-200">
        <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
          <Award className="h-5 w-5 text-indigo-600" /> Supported Citation Styles
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          {(citationStyles || []).map((style: any) => (
            <div key={style.code} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-2">
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">
                {style.code}
              </span>
              <h4 className="font-bold text-slate-900 text-sm">{style.name}</h4>
              <p className="text-xs text-slate-500 line-clamp-2">{style.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
