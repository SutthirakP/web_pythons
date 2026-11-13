"use client";
import { useState } from "react";

type Attempt = {
  id: number;
  method: "HEAD" | "GET";
  ok: boolean;
  text: string;
  at: string;
};

/**
 * Homework: the backend allows every method except HEAD (appm2m/cors.py).
 * HEAD /foo is blocked by the browser's CORS check; GET /foo on the same URL works.
 */
export default function CorsLab({ apiUrl }: { apiUrl: string }) {
  const [attempts, setAttempts] = useState<Attempt[]>([]);
  const [busy, setBusy] = useState(false);

  async function call(method: Attempt["method"]) {
    setBusy(true);
    const at = new Date().toLocaleTimeString("en-GB", { hour12: false });
    let attempt: Omit<Attempt, "id">;

    try {
      const response = await fetch(`${apiUrl}/foo`, { method });
      const detail =
        method === "HEAD"
          ? `X-Foo: ${response.headers.get("X-Foo") ?? "(not exposed)"}`
          : JSON.stringify(await response.json());
      attempt = { method, ok: true, at, text: `${response.status} ${response.statusText} — ${detail}` };
    } catch (error) {
      // The browser hides the real CORS reason from JavaScript: all we get is a
      // TypeError. The full message is in DevTools → Console.
      const message = error instanceof Error ? `${error.name}: ${error.message}` : String(error);
      attempt = {
        method,
        ok: false,
        at,
        text: `Blocked by CORS policy — ${message}. The ${method} method is not allowed for this origin.`,
      };
    }

    setAttempts((current) => [{ id: Date.now(), ...attempt }, ...current].slice(0, 6));
    setBusy(false);
  }

  return (
    <section className="card p-6">
      <div className="mb-1 flex items-center justify-between gap-3">
        <h2 className="text-base font-semibold">CORS test</h2>
        <span className="badge badge-neutral">allow all except HEAD</span>
      </div>
      <p className="mb-4 text-xs text-muted">
        Calls <code>{apiUrl}/foo</code> from this page (a different origin). Open DevTools → Console to
        see the browser&apos;s full CORS message.
      </p>

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => call("HEAD")}
          disabled={busy}
          className="btn btn-primary"
          style={{ width: "auto" }}
        >
          Send HEAD /foo
        </button>
        <button
          type="button"
          onClick={() => call("GET")}
          disabled={busy}
          className="btn btn-ghost"
          style={{ width: "auto" }}
        >
          Send GET /foo
        </button>
      </div>

      {attempts.length > 0 && (
        <ul className="mt-4 flex flex-col gap-2">
          {attempts.map((a) => (
            <li
              key={a.id}
              className={a.ok ? "alert alert-success" : "alert alert-danger"}
              style={{ alignItems: "flex-start" }}
            >
              <span>{a.ok ? "✓" : "✕"}</span>
              <span className="min-w-0">
                <strong>{a.method}</strong> <span className="text-xs opacity-70">{a.at}</span>
                <br />
                <span style={{ overflowWrap: "anywhere" }}>{a.text}</span>
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
