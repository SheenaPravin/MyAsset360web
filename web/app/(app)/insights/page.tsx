"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiGet } from "@/lib/api";
import { getToken } from "@/lib/format";

type Insight = {
  title?: string;
  heading?: string;
  message?: string;
  description?: string;
  severity?: string;
  category?: string;
};

export default function InsightsPage() {
  const router = useRouter();
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    apiGet<Insight[] | { insights: Insight[] }>("/api/analytics/ai-insights")
      .then((d) => setInsights(Array.isArray(d) ? d : d.insights ?? []))
      .catch(() => setError("Failed to load insights."))
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return <p className="text-sm text-slate-500">Loading insights…</p>;
  if (error) return <p className="text-sm text-red-600">{error}</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">AI Insights</h1>
      {insights.length === 0 ? (
        <p className="text-sm text-slate-500">No insights yet.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {insights.map((ins, i) => (
            <div key={i} className="card">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold">{ins.title ?? ins.heading ?? `Insight ${i + 1}`}</h2>
                {(ins.severity || ins.category) && (
                  <span className="text-xs bg-slate-100 rounded px-2 py-1">
                    {ins.severity ?? ins.category}
                  </span>
                )}
              </div>
              <p className="text-sm text-slate-600 mt-2">
                {ins.message ?? ins.description ?? ""}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
