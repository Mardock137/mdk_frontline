import Link from "next/link";

const WEBSITE_URL = process.env.NEXT_PUBLIC_WEBSITE_URL ?? "https://mdk137.com";

const REASON_COPY: Record<string, { title: string; body: string }> = {
  missing_token: {
    title: "Accesso non riuscito",
    body: "Manca il token di accesso. Torna al sito MDK-137 e apri di nuovo l'app.",
  },
  invalid_token: {
    title: "Link scaduto o non valido",
    body: "Il collegamento di accesso non è più valido. Torna al sito e riprova: il link dura solo un minuto.",
  },
  backend_error: {
    title: "Servizio temporaneamente non disponibile",
    body: "Non siamo riusciti a contattare Frontline. Riprova tra poco dal sito MDK-137.",
  },
};

export default async function SsoErrorPage({
  searchParams,
}: {
  searchParams: Promise<{ reason?: string }>;
}) {
  const { reason } = await searchParams;
  const copy =
    REASON_COPY[reason ?? ""] ?? {
      title: "Accesso non riuscito",
      body: "Non è stato possibile aprire la dashboard. Torna al sito MDK-137 e riprova.",
    };

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md rounded-lg border border-gray-200 bg-white p-8 text-center shadow-sm">
        <h1 className="text-xl font-semibold text-gray-900">{copy.title}</h1>
        <p className="mt-3 text-sm text-gray-600">{copy.body}</p>
        <Link
          href={WEBSITE_URL}
          className="mt-6 inline-flex h-9 items-center justify-center rounded-md bg-gray-900 px-4 text-sm font-medium text-white hover:bg-gray-700"
        >
          Torna al sito MDK-137
        </Link>
      </div>
    </main>
  );
}
