export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const q = searchParams.get("q") ?? "";
  const rawLimit = Number(searchParams.get("limit") ?? "5");
  const limit = Number.isFinite(rawLimit) && rawLimit > 0 ? rawLimit : 5;

  const response = await fetch(
    `http://localhost:8000/search/?q=${encodeURIComponent(q)}&limit=${encodeURIComponent(String(limit))}`,
  );

  if (!response.ok) {
    return Response.json(
      { error: "Échec de la recherche" },
      { status: response.status },
    );
  }

  const data = await response.json();
  return Response.json(data);
}
