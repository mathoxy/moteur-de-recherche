type ResultCardProps = {
  type: string;
  title: string;
  date: string;
  excerpt: string;
  score: number;
  as?: "article" | "button";
  onClick?: () => void;
  className?: string;
};

function formatDisplayText(value: string) {
  const decoded = value
    .replace(/\\u([0-9a-fA-F]{4})/g, (_, hex) => {
      try {
        return String.fromCharCode(Number.parseInt(hex, 16));
      } catch {
        return " ";
      }
    })
    .replace(/\\x([0-9a-fA-F]{2})/g, " ")
    .replace(/\\n|\\r|\\t|\\f|\\v/g, " ")
    .replace(
      /[\u0000-\u001F\u007F-\u009F\u00A0\u200B-\u200D\u2060\uFEFF]/g,
      " ",
    )
    .replace(/[\n\r\t\f\v]+/g, " ");

  return decoded.replace(/\s+/g, " ").trim();
}

export default function ResultCard({
  type,
  title,
  date,
  excerpt,
  score,
  as = "article",
  onClick,
  className = "",
}: ResultCardProps) {
  const cleanType = formatDisplayText(type);
  const cleanTitle = formatDisplayText(title);
  const cleanDate = formatDisplayText(date);
  const cleanExcerpt = formatDisplayText(excerpt);

  const content = (
    <>
      <div className="mb-4 flex items-center justify-between gap-3">
        <span className="rounded-full bg-[#eef3ff] px-2 py-1 text-[10px] font-semibold tracking-widest text-[#3647c0]">
          {cleanType}
        </span>
        <span className="text-xs font-semibold text-[#2d3748]">
          ★ {score}% pertinence
        </span>
      </div>

      <h3 className="text-xl font-semibold text-[#1d2431]">{cleanTitle}</h3>
      <p className="mt-3 text-sm text-[#6b7280]">{cleanDate}</p>
      <p className="mt-5 text-sm leading-6 text-[#475467]">{cleanExcerpt}</p>
    </>
  );

  if (as === "button") {
    return (
      <button
        type="button"
        onClick={onClick}
        className={[
          "result-card w-full rounded-[20px] border border-[#dfe3ea] bg-white p-5 text-left transition hover:-translate-y-0.5 hover:border-[#c7d3f8] hover:shadow-sm",
          className,
        ].join(" ")}
      >
        {content}
      </button>
    );
  }

  return (
    <article
      className={[
        "result-card rounded-[20px] border border-[#dfe3ea] bg-white p-5",
        className,
      ].join(" ")}
    >
      {content}
    </article>
  );
}
