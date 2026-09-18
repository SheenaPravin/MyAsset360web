"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";
import { apiGet } from "@/lib/api";
import { formatINR, getToken } from "@/lib/format";
import KpiCard from "@/components/KpiCard";

type DashboardData = {
  net_worth?: number;
  total_assets?: number;
  total_liabilities?: number;
  healthcare_spend?: number;
  health_spend?: number;
  health_spend_total?: number;
  total_sum_insured?: number;
  insurance_coverage?: number;
  total_coverage?: number;
  expense_by_category?: Record<string, number>;
  assets_by_type?: { name?: string; type?: string; value: number }[];
  monthly_trend?: { month?: string; label?: string; value: number }[];
  upcoming_renewals?: { title?: string; name?: string; date?: string; due_date?: string }[];
  notifications?: { message?: string; title?: string }[];
};

type AssetRow = { asset_type?: string; current_value?: number };

const COLORS = ["#2563eb", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"];

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    Promise.all([
      apiGet<DashboardData>("/api/analytics/dashboard"),
      apiGet<AssetRow[]>("/api/assets/").catch(() => [] as AssetRow[]),
    ])
      .then(([d, assets]) => {
        // Build pie data from the asset list (backend has no asset-breakdown endpoint).
        const byType = new Map<string, number>();
        for (const a of assets) {
          const k = a.asset_type || "other";
          byType.set(k, (byType.get(k) ?? 0) + (a.current_value ?? 0));
        }
        const pie: { type: string; value: number }[] = [];
        byType.forEach((value, type) => pie.push({ type, value }));
        d.assets_by_type = pie;
        setData(d);
      })
      .catch(() => setError("Failed to load dashboard."))
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return <p className="text-sm text-slate-500">Loading dashboard…</p>;
  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!data) return <p className="text-sm text-slate-500">No data.</p>;

  const pieData = (data.assets_by_type ?? []).map((a) => ({
    name: a.name ?? a.type ?? "Other",
    value: a.value,
  }));
  const barData = Object.entries(data.expense_by_category ?? {}).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <KpiCard title="Net Worth" value={formatINR(data.net_worth)} />
        <KpiCard title="Total Assets" value={formatINR(data.total_assets)} />
        <KpiCard title="Total Liabilities" value={formatINR(data.total_liabilities)} />
        <KpiCard
          title="Health Spend"
          value={formatINR(data.health_spend ?? data.health_spend_total ?? data.healthcare_spend)}
        />
        <KpiCard
          title="Insurance Coverage"
          value={formatINR(data.insurance_coverage ?? data.total_coverage ?? data.total_sum_insured)}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card">
          <h2 className="font-semibold mb-2">Assets by Type</h2>
          {pieData.length ? (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={100} label>
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v: number) => formatINR(v)} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-slate-500">No asset breakdown.</p>
          )}
        </div>
        <div className="card">
          <h2 className="font-semibold mb-2">Health Spend by Category</h2>
          {barData.length ? (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(v: number) => formatINR(v)} />
                <Bar dataKey="value" fill="#2563eb" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-slate-500">No expense data yet.</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card">
          <h2 className="font-semibold mb-2">Upcoming Renewals</h2>
          {(data.upcoming_renewals ?? []).length ? (
            <ul className="text-sm space-y-1">
              {(data.upcoming_renewals ?? []).map((r, i) => (
                <li key={i} className="flex justify-between border-b last:border-0 py-1">
                  <span>{r.title ?? r.name ?? "Renewal"}</span>
                  <span className="text-slate-500">{r.date ?? r.due_date ?? ""}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-slate-500">No upcoming renewals.</p>
          )}
        </div>
        <div className="card">
          <h2 className="font-semibold mb-2">Notifications</h2>
          {(data.notifications ?? []).length ? (
            <ul className="text-sm space-y-1">
              {(data.notifications ?? []).map((n, i) => (
                <li key={i} className="border-b last:border-0 py-1">
                  {n.message ?? n.title}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-slate-500">No notifications.</p>
          )}
        </div>
      </div>
    </div>
  );
}
