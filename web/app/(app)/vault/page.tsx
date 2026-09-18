"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { apiGet } from "@/lib/api";
import { getToken } from "@/lib/format";
import DataTable from "@/components/DataTable";

type Doc = {
  id?: number;
  title?: string;
  filename?: string;
  file_name?: string;
  created_at?: string;
};

export default function VaultPage() {
  const router = useRouter();
  const [rows, setRows] = useState<Doc[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setRows(await apiGet<Doc[]>("/api/vault/documents"));
    } catch {
      setError("Failed to load documents.");
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

  async function onUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) {
      setError("Choose a file to upload.");
      return;
    }
    setUploading(true);
    setError(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("title", title || file.name);
      await api.post("/api/vault/upload", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setTitle("");
      setFile(null);
      await load();
    } catch {
      setError("Upload failed.");
    } finally {
      setUploading(false);
    }
  }

  if (loading) return <p className="text-sm text-slate-500">Loading vault…</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Vault</h1>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <div className="card">
        <h2 className="font-semibold mb-3">Upload Document</h2>
        <form onSubmit={onUpload} className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label className="label">Title</label>
            <input className="input" value={title}
              onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Sale deed" />
          </div>
          <div>
            <label className="label">File</label>
            <input
              className="input"
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </div>
          <div className="flex items-end">
            <button className="btn-primary" disabled={uploading}>
              {uploading ? "Uploading…" : "Upload"}
            </button>
          </div>
        </form>
      </div>
      <div className="card">
        <h2 className="font-semibold mb-2">Documents</h2>
        <DataTable<Doc>
          columns={[
            { key: "title", header: "Title", render: (r) => r.title ?? r.filename ?? r.file_name ?? "—" },
            { key: "created_at", header: "Uploaded", render: (r) => r.created_at ?? "—" },
          ]}
          rows={rows}
        />
      </div>
    </div>
  );
}
