"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiGet, apiPost, apiErrorMessage } from "@/lib/api";
import { formatINR, getToken } from "@/lib/format";
import DataTable from "@/components/DataTable";

type Policy = {
  id?: number;
  policy_number: string;
  policy_type: string;
  provider: string;
  sum_insured: number;
  premium: number;
  expiry_date?: string;
};

export default function InsurancePage() {
  const router = useRouter();
  const [rows, setRows] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<Policy>({
    policy_number: "",
    policy_type: "health",
    provider: "",
    sum_insured: 0,
    premium: 0,
    expiry_date: "",
  });

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setRows(await apiGet<Policy[]>("/api/insurance/"));
    } catch {
      setError("Failed to load policies.");
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
      await apiPost("/api/insurance/", form);
      setForm({ policy_number: "", policy_type: "health", provider: "", sum_insured: 0, premium: 0, expiry_date: "" });
      await load();
    } catch (e) {
      setError(apiErrorMessage(e, "Failed to create policy."));
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p className="text-sm text-slate-500">Loading insurance…</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Insurance</h1>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <div className="card">
        <h2 className="font-semibold mb-3">Add Policy</h2>
        <form onSubmit={onCreate} className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label className="label">Policy No. / Name</label>
            <input className="input" value={form.policy_number}
              onChange={(e) => setForm({ ...form, policy_number: e.target.value })} required />
          </div>
          <div>
            <label className="label">Type</label>
            <select className="input" value={form.policy_type}
              onChange={(e) => setForm({ ...form, policy_type: e.target.value })}>
              {["health", "life", "motor", "home", "other"].map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Provider</label>
            <input className="input" value={form.provider}
              onChange={(e) => setForm({ ...form, provider: e.target.value })} required />
          </div>
          <div>
            <label className="label">Sum Insured (₹)</label>
            <input className="input" type="number" value={form.sum_insured}
              onChange={(e) => setForm({ ...form, sum_insured: Number(e.target.value) })} required />
          </div>
          <div>
            <label className="label">Premium (₹)</label>
            <input className="input" type="number" value={form.premium}
              onChange={(e) => setForm({ ...form, premium: Number(e.target.value) })} required />
          </div>
          <div>
            <label className="label">Expiry Date</label>
            <input className="input" type="date" value={form.expiry_date ?? ""}
              onChange={(e) => setForm({ ...form, expiry_date: e.target.value })} />
          </div>
          <div className="sm:col-span-3">
            <button className="btn-primary" disabled={saving}>
              {saving ? "Saving…" : "Add Policy"}
            </button>
          </div>
        </form>
      </div>
      <div className="card">
        <h2 className="font-semibold mb-2">Your Policies</h2>
        <DataTable<Policy>
          columns={[
            { key: "policy_number", header: "Policy" },
            { key: "policy_type", header: "Type" },
            { key: "provider", header: "Provider" },
            { key: "sum_insured", header: "Sum Insured", render: (r) => formatINR(r.sum_insured) },
            { key: "premium", header: "Premium", render: (r) => formatINR(r.premium) },
            { key: "expiry_date", header: "Expiry", render: (r) => r.expiry_date ?? "—" },
          ]}
          rows={rows}
        />
      </div>
    </div>
  );
}
