import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "MyAsset360 — Family Wealth & Health",
  description: "Manage your family's wealth. Protect your family's health.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <main className="container py-6">{children}</main>
        <footer className="border-t mt-8">
          <div className="container py-4 text-sm text-slate-500">
            MyAsset360 MVP — Next.js + FastAPI. API:{" "}
            {process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}
          </div>
        </footer>
      </body>
    </html>
  );
}
