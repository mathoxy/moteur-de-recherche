"use client";

import ResultCard from "@/components/ResultCard";
import { FormEvent, useMemo, useState } from "react";

type ResultItem = {
  content: string;
  metadata: {
    title?: string;
    document_type?: string;
    document_number?: string;
    publication_date?: string;
    source_url?: string;
    language?: string;
    article?: string;
    page?: number;
    page_label?: string;
    source?: string;
  };
};

const recentSearches = [
  {
    type: "BULLETIN OFFICIEL",
    title: "Loi n° 2023-105 relative à l’innovation numérique",
    date: "15 Octobre 2023",
    excerpt:
      '"Cette loi définit le cadre juridique pour le développement des systèmes d’intelligence artificielle dans le secteur public."',
    score: 98,
  },
  {
    type: "BULLETIN OFFICIEL",
    title: "Décret d’application n° 2023-442",
    date: "22 Novembre 2023",
    excerpt:
      '"Précise les modalités de contrôle et d’audit pour les plateformes numériques d’énergie ainsi que la vigilance imposée."',
    score: 94,
  },
  {
    type: "BULLETIN OFFICIEL",
    title: "Loi de finances pour l’année 2024",
    date: "30 Décembre 2023",
    excerpt:
      '"Dispositions relatives au soutien fiscal pour les entreprises innovantes et les investissements liés aux technologies"',
    score: 91,
  },
];

export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ResultItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);
  const [periodFilter, setPeriodFilter] = useState("all");
  const [sortMode, setSortMode] = useState("pertinence");
  const [resultLimit, setResultLimit] = useState("5");

  const visibleResults = useMemo(() => {
    if (!results.length) return [];

    const filtered = [...results].filter((item) => {
      if (periodFilter === "all") return true;

      const publicationDate = item.metadata?.publication_date ?? "";
      return publicationDate.startsWith(periodFilter);
    });

    if (sortMode === "date-desc") {
      filtered.sort((a, b) => {
        const dateA = a.metadata?.publication_date ?? "";
        const dateB = b.metadata?.publication_date ?? "";
        return new Date(dateB).getTime() - new Date(dateA).getTime();
      });
    }

    if (sortMode === "date-asc") {
      filtered.sort((a, b) => {
        const dateA = a.metadata?.publication_date ?? "";
        const dateB = b.metadata?.publication_date ?? "";
        return new Date(dateA).getTime() - new Date(dateB).getTime();
      });
    }

    const limit = Number(resultLimit) || 5;
    return filtered.slice(0, limit);
  }, [results, periodFilter, sortMode, resultLimit]);

  async function runSearch(searchQuery: string) {
    const trimmed = searchQuery.trim();

    if (!trimmed) {
      setResults([]);
      setHasSearched(false);
      setError("");
      return;
    }

    setLoading(true);
    setError("");
    setHasSearched(true);
    setQuery(trimmed);

    try {
      const response = await fetch(
        `/api/search?q=${encodeURIComponent(trimmed)}&limit=${encodeURIComponent(resultLimit)}`,
      );
      if (!response.ok) {
        throw new Error("Échec de la recherche");
      }
      const payload = await response.json();
      setResults(Array.isArray(payload?.results) ? payload.results : []);
    } catch (fetchError) {
      setResults([]);
      setError(
        fetchError instanceof Error
          ? fetchError.message
          : "Une erreur est survenue",
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await runSearch(query);
  }

  return (
    <div className="min-h-screen bg-[#f5f5f7] text-slate-800">
      <header className="border-b border-[#dfe3ea] bg-[#f9f9fb]">
        <div className="mx-auto flex w-full max-w-[1200px] items-center justify-between px-6 py-4">
          <a href="/">
            <div className="flex items-center gap-1 text-2xl font-extrabold tracking-tight text-[#2f3b8a]">
              <span className="text-[#2c3b9d]">Lex</span>
              <span className="text-[#5f6ed5]">AI</span>
            </div>
          </a>

          <button
            type="button"
            className="inline-flex items-center gap-2 rounded-full border border-[#dfe3ea] bg-white px-3 py-2 text-sm text-slate-600 shadow-sm transition hover:border-[#c9d3ef] hover:text-slate-800"
          >
            <span className="text-lg">🇫🇷</span>
            <span>Français</span>
            <span className="text-xs text-slate-400">▼</span>
          </button>
        </div>
      </header>

      <main className="mx-auto w-full max-w-[1200px] px-6 pb-10 pt-8">
        <div className="mx-auto max-w-[900px] pt-8 text-center">
          <h1 className="text-4xl font-semibold tracking-[-0.04em] text-[#1f2430] md:text-[3.15rem] md:leading-[1.2]">
            Explorez les textes juridiques avec intelligence et précision.
          </h1>
          <p className="mx-auto mt-4 max-w-[760px] text-base text-[#5d6474] md:text-xl">
            Recherchez dans les lois, les décrets et les bulletins officiels
            grâce au langage naturel et à la recherche sémantique avancée.
          </p>
        </div>

        <form onSubmit={handleSearch} className="mx-auto mt-10 max-w-[860px]">
          <div className="search-shadow flex items-center gap-3 rounded-[18px] border border-[#cfd7e6] bg-white px-4 py-3 shadow-sm">
            <span className="text-xl">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                height="24px"
                viewBox="0 -960 960 960"
                width="24px"
                fill="#cfd7e6"
              >
                <path d="M784-120 532-372q-30 24-69 38t-83 14q-109 0-184.5-75.5T120-580q0-109 75.5-184.5T380-840q109 0 184.5 75.5T640-580q0 44-14 83t-38 69l252 252-56 56ZM380-400q75 0 127.5-52.5T560-580q0-75-52.5-127.5T380-760q-75 0-127.5 52.5T200-580q0 75 52.5 127.5T380-400Z" />
              </svg>
            </span>
            <input
              aria-label="Recherche juridique"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Poser une question juridique..."
              className="flex-1 border-none bg-transparent text-lg text-slate-700 outline-none placeholder:text-slate-400"
            />
            <button
              type="submit"
              disabled={loading}
              className="rounded-xl bg-[#2f3d9e] px-5 py-3 text-base font-medium text-white transition hover:bg-[#27378d] disabled:cursor-not-allowed disabled:opacity-70"
            >
              {loading ? "Recherche..." : "Rechercher"}
            </button>
          </div>

          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <SelectFilter
              label="Période"
              value={periodFilter}
              options={[
                { value: "all", label: "Toutes" },
                { value: "2026", label: "2026" },
                { value: "2025", label: "2025" },
                { value: "2024", label: "2024" },
                { value: "2023", label: "2023" },
              ]}
              onChange={(value) => setPeriodFilter(value)}
            />
            <SelectFilter
              label="Trier par"
              value={sortMode}
              options={[
                { value: "pertinence", label: "Pertinence" },
                { value: "date-desc", label: "Date récente" },
                { value: "date-asc", label: "Date ancienne" },
              ]}
              onChange={(value) => setSortMode(value)}
            />
            <SelectFilter
              label="Nombre de résultats max"
              value={resultLimit}
              options={[
                { value: "3", label: "3 résultats" },
                { value: "5", label: "5 résultats" },
                { value: "10", label: "10 résultats" },
                { value: "15", label: "15 résultats" },
              ]}
              onChange={(value) => setResultLimit(value)}
            />
          </div>
        </form>

        {error ? (
          <div className="mx-auto mt-12 max-w-[500px] rounded-2xl border border-red-200 bg-red-50 p-4 text-center text-sm text-red-700">
            {error}
          </div>
        ) : null}

        {visibleResults.length > 0 ? (
          <section className="mx-auto mt-16 max-w-[1100px]">
            <div className="mb-8 text-center">
              <h2 className="text-3xl font-semibold text-[#1f2430]">
                Résultats de recherche
              </h2>
              <p className="mt-2 text-base text-[#667085]">
                Les documents les plus pertinents pour votre requête sont listés
                ci-dessous.
              </p>
            </div>

            <div className="grid gap-5 md:grid-cols-3">
              {visibleResults.map((item, index) => {
                const metadata = item.metadata ?? {};
                const type = (
                  metadata.document_type ?? "Bulletin officiel"
                ).toUpperCase();
                const score = Math.max(80, 90 - index * 2);
                const title = metadata.title || "Document juridique";
                const excerpt =
                  item.content?.slice(0, 200) || "Aucun extrait disponible.";

                return (
                  <ResultCard
                    key={`${title}-${index}`}
                    type={type}
                    title={title}
                    date={metadata.publication_date || "Date non précisée"}
                    excerpt={`${excerpt}...`}
                    score={score}
                  />
                );
              })}
            </div>
          </section>
        ) : null}

        {!hasSearched && !loading && !error ? (
          <section className="mx-auto mt-16 max-w-[1100px]">
            <div className="mb-8 text-center">
              <h2 className="text-3xl font-semibold text-[#1f2430]">
                Exemple de recherches
              </h2>
            </div>

            <div className="grid gap-5 md:grid-cols-3">
              {recentSearches.map((item) => (
                <ResultCard
                  key={item.title}
                  type={item.type}
                  title={item.title}
                  date={item.date}
                  excerpt={item.excerpt}
                  score={item.score}
                  as="button"
                  onClick={() => runSearch(item.title)}
                />
              ))}
            </div>
          </section>
        ) : null}
      </main>

      <footer className="mt-10 border-t border-[#dfe3ea] bg-[#f9f9fb]">
        <div className="mx-auto flex w-full max-w-[1200px] items-center justify-between gap-4 px-6 py-5 text-sm text-slate-500">
          <div className="font-bold tracking-[-0.03em] text-[#2f3d9e]">
            LexAI
          </div>
          <div className="text-slate-900">
            © 2024 LexAI Legal Technologies. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}

function SelectFilter({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: Array<{ value: string; label: string }>;
  onChange: (value: string) => void;
}) {
  return (
    <div className="group relative inline-flex items-center gap-2 rounded-full border border-[#dfe3ea] bg-white px-3 py-2.5 text-sm shadow-sm transition-all duration-200 hover:border-[#bfcdfd] hover:shadow-md">
      <span className="font-medium text-slate-600">{label}</span>
      <div className="relative">
        <select
          value={value}
          onChange={(event) => onChange(event.target.value)}
          className="appearance-none cursor-pointer rounded-full border border-transparent bg-transparent pr-7 pl-1 text-sm font-medium text-slate-700 outline-none transition-colors focus:border-[#cdd9ff] focus:bg-[#f8faff]"
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <span className="pointer-events-none absolute inset-y-0 right-2 flex items-center text-xs text-slate-500">
          ▾
        </span>
      </div>
    </div>
  );
}
