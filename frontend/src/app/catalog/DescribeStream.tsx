"use client";
import { useEffect, useRef, useState } from "react";

type Status = "connecting" | "thinking" | "streaming" | "done" | "error";

/**
 * Streaming homework: reads GET /products/{id}/describe (Server-Sent Events) with
 * the browser's EventSource and shows each word the moment it arrives.
 */
export default function DescribeStream({
  apiUrl,
  productId,
  canSave,
  onUse,
  onClose,
}: {
  apiUrl: string;
  productId: number;
  canSave: boolean;
  onUse: (text: string) => Promise<void>;
  onClose: () => void;
}) {
  const [run, setRun] = useState(0); // bump to stream a new version
  const [text, setText] = useState("");
  const [status, setStatus] = useState<Status>("connecting");
  const [words, setWords] = useState({ got: 0, total: 0 });
  const [timing, setTiming] = useState<{ first: number | null; total: number | null }>({
    first: null,
    total: null,
  });
  const [saving, setSaving] = useState(false);
  const sourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    const started = performance.now();
    const source = new EventSource(`${apiUrl}/products/${productId}/describe`);
    sourceRef.current = source;

    source.addEventListener("start", (event) => {
      const { words: total } = JSON.parse(event.data);
      setText("");
      setWords({ got: 0, total });
      setTiming({ first: null, total: null });
      setStatus("thinking");
    });

    source.addEventListener("token", (event) => {
      const word: string = JSON.parse(event.data);
      setStatus("streaming");
      setText((current) => current + word);
      setWords((current) => ({ ...current, got: current.got + 1 }));
      setTiming((current) =>
        current.first === null ? { ...current, first: Math.round(performance.now() - started) } : current
      );
    });

    source.addEventListener("done", () => {
      // close it ourselves - otherwise EventSource reconnects and streams again
      source.close();
      setStatus("done");
      setTiming((current) => ({ ...current, total: Math.round(performance.now() - started) }));
    });

    source.onerror = () => {
      source.close();
      setStatus((current) => (current === "done" ? current : "error"));
    };

    return () => source.close();
  }, [apiUrl, productId, run]);

  function stop() {
    sourceRef.current?.close();
    setStatus("done");
  }

  function regenerate() {
    setStatus("connecting");
    setRun((n) => n + 1);
  }

  async function use() {
    setSaving(true);
    try {
      await onUse(text.trim());
    } finally {
      setSaving(false);
    }
  }

  const live = status === "connecting" || status === "thinking" || status === "streaming";
  const label = {
    connecting: "Connecting…",
    thinking: "Thinking…",
    streaming: `Writing… ${words.got}/${words.total} words`,
    done: `Done · ${words.got} words`,
    error: "Stream failed — is the backend on port 8002 running?",
  }[status];

  return (
    <div className="describe-panel">
      <div className="describe-head">
        <span className={live ? "describe-dot live" : "describe-dot"} />
        <span className="text-xs font-semibold">✨ {label}</span>
        {timing.first !== null && (
          <span className="describe-timing">
            first word {timing.first} ms{timing.total !== null && ` · all ${timing.total} ms`}
          </span>
        )}
      </div>

      <p className="describe-text">
        {text}
        {live && <span className="describe-caret" />}
        {status === "thinking" && text === "" && (
          <span className="chat-typing" aria-label="Thinking">
            <span />
            <span />
            <span />
          </span>
        )}
      </p>

      {words.total > 0 && (
        <div className="describe-progress">
          <span style={{ width: `${(words.got / words.total) * 100}%` }} />
        </div>
      )}

      <div className="flex flex-wrap justify-end gap-2">
        {live ? (
          <button type="button" onClick={stop} className="btn btn-ghost" style={{ width: "auto" }}>
            Stop
          </button>
        ) : (
          <>
            <button type="button" onClick={onClose} className="btn btn-ghost" style={{ width: "auto" }}>
              Close
            </button>
            <button type="button" onClick={regenerate} className="btn btn-ghost" style={{ width: "auto" }}>
              ↻ Regenerate
            </button>
            <button
              type="button"
              onClick={use}
              disabled={!canSave || saving || text.trim() === ""}
              className="btn btn-primary"
              style={{ width: "auto" }}
            >
              {!canSave ? "Log in to save" : saving ? "Saving…" : "Use as description"}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
