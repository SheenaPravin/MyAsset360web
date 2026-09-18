"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiGet, apiPost, apiErrorMessage } from "@/lib/api";
import { formatINR, getToken } from "@/lib/format";
import DataTable from "@/components/DataTable";

type Loan = {
  id?: number;
  lender: string;
  loan_type: string;
  principal: number;
  outstanding: number;
  interest_rate?: number;
  emi?: number;
};

export default function LoansPage() {
  const router = useRouter();
  const [rows, setRows] = useState<Loan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<Loan>({
    lender: "",
    loan_type: "home",
    principal: 0,
    outstanding: 0,
    interest_rate: 8.5,
    emi: 0,
  });

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setRows(await apiGet<Loan[]>("/api/loans/"));
    } catch {
      setError("Failed to load loans.");
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
      await apiPost("/api/loans/", form);
      setForm({ lender: "", loan_type: "home", principal: 0, outstanding: 0, interest_rate: 8.5, emi: 0 });
      await load();
    } catch (e) {
      setError(apiErrorMessage(e, "Failed to create loan."));
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p className="text-sm text-slate-500">Loading loans…</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Loans</h1>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <div className="card">
        <h2 className="font-semibold mb-3">Add Loan</h2>
        <form onSubmit={onCreate} className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label className="label">Lender</label>
            <input className="input" value={form.lender}
              onChange={(e) => setForm({ ...form, lender: e.target.value })} required />
          </div>
          <div>
            <label className="label">Loan Type</label>
            <select className="input" value={form.loan_type}
              onChange={(e) => setForm({ ...form, loan_type: e.target.value })}>
              {["home", "car", "personal", "education", "other"].map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Principal (₹)</label>
            <input className="input" type="number" value={form.principal}
              onChange={(e) => setForm({ ...form, principal: Number(e.target.value) })} required />
          </div>
          <div>
            <label className="label">Outstanding (₹)</label>
            <input className="input" type="number" value={form.outstanding}
              onChange={(e) => setForm({ ...form, outstanding: Number(e.target.value) })} required />
          </div>
          <div>
            <label className="label">Interest %</label>
            <input className="input" type="number" step="0.01" value={form.interest_rate ?? 0}
              onChange={(e) => setForm({ ...form, interest_rate: Number(e.target.value) })} />
          </div>
          <div>
            <label className="label">EMI (₹)</label>
            <input className="input" type="number" value={form.emi ?? 0}
              onChange={(e) => setForm({ ...form, emi: Number(e.target.value) })} />
          </div>
          <div className="sm:col-span-3">
            <button className="btn-primary" disabled={saving}>
              {saving ? "Saving…" : "Add Loan"}
            </button>
          </div>
        </form>
      </div>
      <div className="card">
        <h2 className="font-semibold mb-2">Your Loans</h2>
        <DataTable<Loan>
          columns={[
            { key: "lender", header: "Lender" },
            { key: "loan_type", header: "Type" },
            { key: "principal", header: "Principal", render: (r) => formatINR(r.principal) },
            { key: "outstanding", header: "Outstanding", render: (r) => formatINR(r.outstanding) },
            { key: "interest_rate", header: "Rate %", render: (r) => String(r.interest_rate ?? "—") },
            { key: "emi", header: "EMI", render: (r) => formatINR(r.emi) },
          ]}
          rows={rows}
        />
      </div>
    </div>
  );
}
