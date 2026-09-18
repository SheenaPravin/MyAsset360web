import Link from "next/link";

const modules = [
  { title: "Assets", href: "/assets", desc: "Real estate, gold, mutual funds, stocks — one portfolio view." },
  { title: "Loans", href: "/loans", desc: "Track EMIs, interest burden and payoff progress." },
  { title: "Insurance", href: "/insurance", desc: "Policies, coverage and premium renewals in one place." },
  { title: "Health", href: "/health", desc: "Family profiles, medical records and health spend." },
  { title: "Vault", href: "/vault", desc: "Encrypted document locker for deeds, policies, reports." },
  { title: "AI Insights", href: "/insights", desc: "Net-worth trends, spend anomalies, renewal nudges." },
  { title: "Dashboard", href: "/dashboard", desc: "Net worth, liabilities and coverage at a glance." },
  { title: "Secure Login", href: "/login", desc: "JWT-secured access backed by your FastAPI backend." },
];

export default function Home() {
  return (
    <div>
      <section className="card text-center py-12">
        <h1 className="text-3xl md:text-5xl font-bold">
          Manage Your Family&apos;s Wealth. Protect Your Family&apos;s Health.
        </h1>
        <p className="mt-4 text-slate-600 max-w-2xl mx-auto">
          MyAsset360 unifies assets, loans, insurance, health and documents
          into a single family dashboard powered by FastAPI + Next.js.
        </p>
        <div className="mt-6 flex gap-3 justify-center">
          <Link href="/dashboard" className="btn-primary">
            Go to Dashboard
          </Link>
          <Link href="/login" className="btn-secondary">
            Login
          </Link>
        </div>
      </section>

      <section className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {modules.map((m) => (
          <Link key={m.title} href={m.href} className="card hover:shadow-md">
            <h3 className="font-semibold text-lg">{m.title}</h3>
            <p className="text-sm text-slate-600 mt-1">{m.desc}</p>
          </Link>
        ))}
      </section>

      <section className="card mt-8">
        <h2 className="font-semibold text-lg">Architecture</h2>
        <p className="text-sm text-slate-600 mt-2">
          Next.js 14 (App Router) frontend talks to FastAPI at{" "}
          <code>NEXT_PUBLIC_API_URL</code> (default{" "}
          <code>http://localhost:8000</code>). JWT from{" "}
          <code>POST /api/auth/login</code> is stored in{" "}
          <code>localStorage</code> and attached as a Bearer token on every
          request. Dashboards read from <code>/api/analytics/*</code>;
          CRUD pages use per-module routers.
        </p>
      </section>
    </div>
  );
}
