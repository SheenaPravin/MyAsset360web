"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiGet, apiPost, apiErrorMessage } from "@/lib/api";
import { formatINR, getToken } from "@/lib/format";
import DataTable from "@/components/DataTable";

type Asset = {
  id?: number;
  title: string;
  asset_type: string;
  current_value: number;
  purchase_value?: number;
};

const ASSET_TYPES = ["real_estate", "gold", "mutual_fund", "stock", "fd", "other"];

export default function AssetsPage() {
  const router = useRouter();
  const [rows, setRows] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<Asset>({
    title: "",
    asset_type: "mutual_fund",
    current_value: 0,
    purchase_value: 0,
  });
  const [saving, setSaving] = useState(false);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await apiGet<Asset[]>("/api/assets/");
      setRows(data);
    } catch {
      setError("Failed to load assets.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    load();
  }, [router]);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await apiPost("/api/assets/", form);
      setForm({ title: "", asset_type: "mutual_fund", current_value: 0, purchase_value: 0 });
      await load();
    } catch (e) {
      setError(apiErrorMessage(e, "Failed to create asset."));
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p className="text-sm text-slate-500">Loading assets…</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Assets</h1>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <div className="card">
        <h2 className="font-semibold mb-3">Add Asset</h2>
        <form onSubmit={onCreate} className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <div>
            <label className="label">Title</label>
            <input className="input" value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })} required />
          </div>
          <div>
            <label className="label">Type</label>
            <select className="input" value={form.asset_type}
              onChange={(e) => setForm({ ...form, asset_type: e.target.value })}>
              {ASSET_TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Current Value (₹)</label>
            <input className="input" type="number" value={form.current_value}
              onChange={(e) => setForm({ ...form, current_value: Number(e.target.value) })} required />
          </div>
          <div>
            <label className="label">Purchase Value (₹)</label>
            <input className="input" type="number" value={form.purchase_value ?? 0}
              onChange={(e) => setForm({ ...form, purchase_value: Number(e.target.value) })} />
          </div>
          <div className="sm:col-span-4">
            <button className="btn-primary" disabled={saving}>
              {saving ? "Saving…" : "Add Asset"}
            </button>
          </div>
        </form>
      </div>
      <div className="card">
        <h2 className="font-semibold mb-2">Your Assets</h2>
        <DataTable<Asset>
          columns={[
            { key: "title", header: "Title" },
            { key: "asset_type", header: "Type" },
            { key: "current_value", header: "Current Value", render: (r) => formatINR(r.current_value) },
            { key: "purchase_value", header: "Purchase Value", render: (r) => formatINR(r.purchase_value) },
          ]}
          rows={rows}
        />
      </div>
    </div>
  );
}
