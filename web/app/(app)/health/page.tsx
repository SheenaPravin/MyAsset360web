"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiGet, apiPost, apiErrorMessage } from "@/lib/api";
import { formatINR, getToken } from "@/lib/format";
import DataTable from "@/components/DataTable";

type Expense = {
  id?: number;
  hospital?: string;
  notes?: string;
  amount: number;
  category?: string;
  expense_date?: string;
};

type HealthRecord = {
  id?: number;
  title: string;
  record_type?: string;
  visit_date?: string;
  hospital?: string;
  doctor?: string;
  notes?: string;
};

export default function HealthPage() {
  const router = useRouter();
  const [tab, setTab] = useState<"expenses" | "records">("expenses");
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [records, setRecords] = useState<HealthRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<Expense>({
    hospital: "",
    amount: 0,
    category: "general",
    expense_date: "",
    notes: "",
  });
  const [recForm, setRecForm] = useState<HealthRecord>({
    title: "",
    record_type: "general",
    visit_date: "",
    hospital: "",
    doctor: "",
    notes: "",
  });

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [ex, rec] = await Promise.all([
        apiGet<Expense[]>("/api/health/expenses"),
        apiGet<HealthRecord[]>("/api/health/records"),
      ]);
      setExpenses(ex);
      setRecords(rec);
    } catch {
      setError("Failed to load health data.");
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
      await apiPost("/api/health/expenses", form);
      setForm({ hospital: "", amount: 0, category: "general", expense_date: "", notes: "" });
      await load();
    } catch (e) {
      setError(apiErrorMessage(e, "Failed to add expense."));
    } finally {
      setSaving(false);
    }
  }

  async function onCreateRecord(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await apiPost("/api/health/records", recForm);
      setRecForm({ title: "", record_type: "general", visit_date: "", hospital: "", doctor: "", notes: "" });
      await load();
    } catch (e) {
      setError(apiErrorMessage(e, "Failed to add record."));
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p className="text-sm text-slate-500">Loading health…</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Health</h1>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <div className="flex gap-2">
        <button
          className={tab === "expenses" ? "btn-primary" : "btn-secondary"}
          onClick={() => setTab("expenses")}
        >
          Expenses
        </button>
        <button
          className={tab === "records" ? "btn-primary" : "btn-secondary"}
          onClick={() => setTab("records")}
        >
          Records
        </button>
      </div>

      {tab === "expenses" ? (
        <>
          <div className="card">
            <h2 className="font-semibold mb-3">Add Expense</h2>
            <form onSubmit={onCreate} className="grid grid-cols-1 sm:grid-cols-4 gap-3">
              <div>
                <label className="label">Hospital / Title</label>
                <input className="input" value={form.hospital ?? ""}
                  onChange={(e) => setForm({ ...form, hospital: e.target.value })} required />
              </div>
              <div>
                <label className="label">Amount (₹)</label>
                <input className="input" type="number" value={form.amount}
                  onChange={(e) => setForm({ ...form, amount: Number(e.target.value) })} required />
              </div>
              <div>
                <label className="label">Category</label>
                <input className="input" value={form.category ?? ""}
                  onChange={(e) => setForm({ ...form, category: e.target.value })} />
              </div>
              <div>
                <label className="label">Date</label>
                <input className="input" type="date" value={form.expense_date ?? ""}
                  onChange={(e) => setForm({ ...form, expense_date: e.target.value })} />
              </div>
              <div className="sm:col-span-4">
                <label className="label">Notes</label>
                <input className="input" value={form.notes ?? ""}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })} />
              </div>
              <div className="sm:col-span-4">
                <button className="btn-primary" disabled={saving}>
                  {saving ? "Saving…" : "Add Expense"}
                </button>
              </div>
            </form>
          </div>
          <div className="card">
            <h2 className="font-semibold mb-2">Expenses</h2>
            <DataTable<Expense>
              columns={[
                { key: "hospital", header: "Hospital", render: (r) => r.hospital || "—" },
                { key: "amount", header: "Amount", render: (r) => formatINR(r.amount) },
                { key: "category", header: "Category", render: (r) => r.category ?? "—" },
                { key: "expense_date", header: "Date", render: (r) => r.expense_date ?? "—" },
                { key: "notes", header: "Notes", render: (r) => r.notes || "—" },
              ]}
              rows={expenses}
            />
          </div>
        </>
      ) : (
        <>
          <div className="card">
            <h2 className="font-semibold mb-3">Add Medical Record</h2>
            <form onSubmit={onCreateRecord} className="grid grid-cols-1 sm:grid-cols-4 gap-3">
              <div>
                <label className="label">Title</label>
                <input className="input" value={recForm.title}
                  onChange={(e) => setRecForm({ ...recForm, title: e.target.value })} required />
              </div>
              <div>
                <label className="label">Type</label>
                <input className="input" value={recForm.record_type ?? ""}
                  onChange={(e) => setRecForm({ ...recForm, record_type: e.target.value })} />
              </div>
              <div>
                <label className="label">Visit Date</label>
                <input className="input" type="date" value={recForm.visit_date ?? ""}
                  onChange={(e) => setRecForm({ ...recForm, visit_date: e.target.value })} />
              </div>
              <div>
                <label className="label">Hospital</label>
                <input className="input" value={recForm.hospital ?? ""}
                  onChange={(e) => setRecForm({ ...recForm, hospital: e.target.value })} />
              </div>
              <div>
                <label className="label">Doctor</label>
                <input className="input" value={recForm.doctor ?? ""}
                  onChange={(e) => setRecForm({ ...recForm, doctor: e.target.value })} />
              </div>
              <div className="sm:col-span-3">
                <label className="label">Notes</label>
                <input className="input" value={recForm.notes ?? ""}
                  onChange={(e) => setRecForm({ ...recForm, notes: e.target.value })} />
              </div>
              <div className="sm:col-span-4">
                <button className="btn-primary" disabled={saving}>
                  {saving ? "Saving…" : "Add Record"}
                </button>
              </div>
            </form>
          </div>
          <div className="card">
            <h2 className="font-semibold mb-2">Medical Records</h2>
            <DataTable<HealthRecord>
              columns={[
                { key: "title", header: "Title" },
                { key: "record_type", header: "Type", render: (r) => r.record_type ?? "—" },
                { key: "visit_date", header: "Visit Date", render: (r) => r.visit_date ?? "—" },
                { key: "hospital", header: "Hospital", render: (r) => r.hospital || "—" },
              ]}
              rows={records}
            />
          </div>
        </>
      )}
    </div>
  );
}
