"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { clearToken, getToken } from "@/lib/format";

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/assets", label: "Assets" },
  { href: "/loans", label: "Loans" },
  { href: "/insurance", label: "Insurance" },
  { href: "/health", label: "Health" },
  { href: "/vault", label: "Vault" },
  { href: "/insights", label: "AI Insights" },
];

export default function Navbar() {
  const router = useRouter();
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    setAuthed(!!getToken());
  }, []);

  return (
    <header className="border-b bg-white">
      <div className="container flex items-center justify-between py-3">
        <Link href="/" className="font-bold text-xl text-brand-700">
          MyAsset360
        </Link>
        <nav className="flex flex-wrap gap-3 text-sm">
          {links.map((l) => (
            <Link key={l.href} href={l.href} className="hover:text-brand-600">
              {l.label}
            </Link>
          ))}
          {authed ? (
            <button
              className="hover:text-brand-600"
              onClick={() => {
                clearToken();
                setAuthed(false);
                router.push("/login");
              }}
            >
              Logout
            </button>
          ) : (
            <Link href="/login" className="hover:text-brand-600">
              Login
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
