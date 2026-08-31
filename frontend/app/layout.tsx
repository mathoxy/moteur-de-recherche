import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LexAI | Recherche juridique",
  description: "Moteur de recherche intelligent pour les lois marocaines",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fr" className="h-full antialiased">
      <body className="min-h-full bg-[#f5f5f7] text-slate-800">{children}</body>
    </html>
  );
}
