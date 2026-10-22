"use client";
import { FormEvent, useCallback, useEffect, useRef, useState } from "react";

const WS_URL = "ws://127.0.0.1:8002/ws/chat";
const FILE_URL = "http://127.0.0.1:8002/file";
const MAX_FRAMES = 150;

type ChatProduct = {
  id: number;
  name: string;
  description: string | null;
  price: number;
  image: string | null;
  categories: string[];
};

type ChatMessage =
  | { kind: "bot"; id: string; text: string; products: ChatProduct[]; streaming: boolean }
  | { kind: "user"; id: string; text: string }
  | { kind: "notify"; id: string; text: string; event: "created" | "updated" | "deleted" };

type Frame = { dir: "in" | "out"; at: string; data: string };

type Status = "connecting" | "open" | "closed";

function formatPrice(price: number) {
  return `$${price.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function nowLabel() {
  return new Date().toLocaleTimeString("en-GB", { hour12: false });
}

function ChatIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M4 5.5A2.5 2.5 0 0 1 6.5 3h11A2.5 2.5 0 0 1 20 5.5v8a2.5 2.5 0 0 1-2.5 2.5H10l-4.2 3.6c-.5.4-1.3.1-1.3-.6V16A2.5 2.5 0 0 1 4 13.5v-8Z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
      <circle cx="8.5" cy="9.5" r="1.1" fill="currentColor" />
      <circle cx="12" cy="9.5" r="1.1" fill="currentColor" />
      <circle cx="15.5" cy="9.5" r="1.1" fill="currentColor" />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M6 6l12 12M18 6 6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function SendIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M5 12h13M13 6l6 6-6 6"
        stroke="currentColor"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default function ChatWidget({ onCatalogChanged }: { onCatalogChanged?: () => void }) {
  const [open, setOpen] = useState(false);
  const [showTeaser, setShowTeaser] = useState(false);
  const [view, setView] = useState<"chat" | "frames">("chat");
  const [status, setStatus] = useState<Status>("connecting");
  const [online, setOnline] = useState(0);
  const [latency, setLatency] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [typing, setTyping] = useState(false);
  const [unread, setUnread] = useState(0);
  const [frames, setFrames] = useState<Frame[]>([]);
  const [draft, setDraft] = useState("");

  const socketRef = useRef<WebSocket | null>(null);
  const openRef = useRef(open);
  const onChangedRef = useRef(onCatalogChanged);
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  function toggle(next: boolean) {
    openRef.current = next;
    setOpen(next);
    if (next) {
      setUnread(0);
      setShowTeaser(false);
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }

  useEffect(() => {
    onChangedRef.current = onCatalogChanged;
  }, [onCatalogChanged]);

  const logFrame = useCallback((dir: Frame["dir"], data: string) => {
    setFrames((prev) => [...prev.slice(-(MAX_FRAMES - 1)), { dir, at: nowLabel(), data }]);
  }, []);

  const send = useCallback(
    (payload: object) => {
      const socket = socketRef.current;
      if (!socket || socket.readyState !== WebSocket.OPEN) return false;
      const data = JSON.stringify(payload);
      socket.send(data);
      logFrame("out", data);
      return true;
    },
    [logFrame]
  );

  // One socket for the whole page, opened on load (not only when the window is
  // open) so product notifications still arrive and show up as an unread badge.
  useEffect(() => {
    let stopped = false;
    let retry = 0;
    let retryTimer: ReturnType<typeof setTimeout> | undefined;
    let pingTimer: ReturnType<typeof setInterval> | undefined;

    function handle(raw: string) {
      const msg = JSON.parse(raw);

      switch (msg.type) {
        case "welcome":
          setMessages((prev) =>
            prev.length > 0
              ? prev
              : [{ kind: "bot", id: "welcome", text: msg.text, products: [], streaming: false }]
          );
          setSuggestions(msg.suggestions);
          break;
        case "presence":
          setOnline(msg.online);
          break;
        case "pong":
          setLatency(Math.round(performance.now() - msg.sent));
          break;
        case "typing":
          setTyping(true);
          break;
        case "start":
          setTyping(false);
          setMessages((prev) => [
            ...prev,
            { kind: "bot", id: `bot-${msg.id}-${Date.now()}`, text: "", products: [], streaming: true },
          ]);
          break;
        case "delta":
          setMessages((prev) => {
            const last = prev[prev.length - 1];
            if (!last || last.kind !== "bot" || !last.streaming) return prev;
            return [...prev.slice(0, -1), { ...last, text: last.text + msg.text }];
          });
          break;
        case "end":
          setMessages((prev) => {
            const last = prev[prev.length - 1];
            if (!last || last.kind !== "bot") return prev;
            return [...prev.slice(0, -1), { ...last, products: msg.products, streaming: false }];
          });
          setSuggestions(msg.suggestions);
          if (!openRef.current) setUnread((n) => n + 1);
          break;
        case "notify":
          setMessages((prev) => [
            ...prev,
            { kind: "notify", id: `n-${Date.now()}-${Math.random()}`, text: msg.text, event: msg.event },
          ]);
          if (!openRef.current) setUnread((n) => n + 1);
          onChangedRef.current?.();
          break;
      }
    }

    function connect() {
      setStatus("connecting");
      const socket = new WebSocket(WS_URL);
      socketRef.current = socket;

      socket.onopen = () => {
        retry = 0;
        setStatus("open");
        const ping = () => {
          if (socket.readyState !== WebSocket.OPEN) return;
          const data = JSON.stringify({ type: "ping", sent: performance.now() });
          socket.send(data);
          logFrame("out", data);
        };
        ping();
        pingTimer = setInterval(ping, 10000);
      };

      socket.onmessage = (event) => {
        logFrame("in", event.data);
        try {
          handle(event.data);
        } catch (error) {
          console.error("Bad chat frame", error);
        }
      };

      socket.onclose = () => {
        clearInterval(pingTimer);
        setTyping(false);
        setStatus("closed");
        setOnline(0);
        setLatency(null);
        if (stopped) return;
        // back off 1s, 2s, 4s, ... up to 10s so a stopped backend isn't hammered
        const delay = Math.min(1000 * 2 ** retry, 10000);
        retry += 1;
        retryTimer = setTimeout(connect, delay);
      };
    }

    connect();
    return () => {
      stopped = true;
      clearTimeout(retryTimer);
      clearInterval(pingTimer);
      socketRef.current?.close();
    };
  }, [logFrame]);

  // The "anything I can help with?" bubble that pops out next to the button.
  useEffect(() => {
    const timer = setTimeout(() => {
      if (!openRef.current) setShowTeaser(true);
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const box = scrollRef.current;
    if (box) box.scrollTo({ top: box.scrollHeight, behavior: "smooth" });
  }, [messages, typing, view, open]);

  function ask(text: string) {
    const trimmed = text.trim();
    if (!trimmed) return;
    if (!send({ type: "message", text: trimmed })) return;
    setMessages((prev) => [...prev, { kind: "user", id: `u-${Date.now()}`, text: trimmed }]);
    setDraft("");
    setView("chat");
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    ask(draft);
  }

  const busy = typing || messages.some((m) => m.kind === "bot" && m.streaming);
  const statusText =
    status === "open"
      ? `ออนไลน์ · ${online} คนในแชท${latency !== null ? ` · ${latency} ms` : ""}`
      : status === "connecting"
        ? "กำลังเชื่อมต่อ…"
        : "หลุดการเชื่อมต่อ · กำลังลองใหม่";

  return (
    <div className="chat-root">
      {open && (
        <section className="chat-panel" role="dialog" aria-label="Catalog assistant">
          <header className="chat-header">
            <div className="chat-bot-avatar" aria-hidden="true">
              <ChatIcon />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-bold leading-tight">Catalog Assistant</p>
              <p className="chat-status">
                <span className={`chat-dot chat-dot-${status}`} />
                {statusText}
              </p>
            </div>
            <button
              type="button"
              className={view === "frames" ? "chat-head-btn active" : "chat-head-btn"}
              onClick={() => setView((v) => (v === "chat" ? "frames" : "chat"))}
              title="ดู WebSocket frames ที่รับส่งจริง"
            >
              {"</>"}
            </button>
            <button
              type="button"
              className="chat-head-btn"
              onClick={() => toggle(false)}
              aria-label="Close chat"
            >
              <CloseIcon />
            </button>
          </header>

          {view === "chat" ? (
            <div ref={scrollRef} className="chat-body">
              {messages.map((m) =>
                m.kind === "notify" ? (
                  <div key={m.id} className={`chat-notify chat-notify-${m.event}`}>
                    {m.text}
                  </div>
                ) : m.kind === "user" ? (
                  <div key={m.id} className="chat-row chat-row-user">
                    <div className="chat-bubble chat-bubble-user">{m.text}</div>
                  </div>
                ) : (
                  <div key={m.id} className="chat-row">
                    <div className="chat-bubble chat-bubble-bot">
                      {m.text}
                      {m.streaming && <span className="chat-caret" />}
                      {m.products.length > 0 && (
                        <ul className="chat-products">
                          {m.products.map((p) => (
                            <li key={p.id} className="chat-product">
                              {p.image && (
                                // eslint-disable-next-line @next/next/no-img-element -- served by the FastAPI backend, not Next
                                <img src={`${FILE_URL}/${p.image}`} alt={p.name} className="chat-product-img" />
                              )}
                              <div className="min-w-0 flex-1">
                              <div className="flex items-start justify-between gap-2">
                                <span className="font-semibold">{p.name}</span>
                                <span className="chat-price">{formatPrice(p.price)}</span>
                              </div>
                              {p.description && <p className="text-muted text-xs">{p.description}</p>}
                              {p.categories.length > 0 && (
                                <div className="mt-1 flex flex-wrap gap-1">
                                  {p.categories.map((c) => (
                                    <button
                                      key={c}
                                      type="button"
                                      className="chat-tag"
                                      onClick={() => ask(`สินค้าหมวด ${c}`)}
                                    >
                                      {c}
                                    </button>
                                  ))}
                                </div>
                              )}
                              </div>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>
                )
              )}
              {typing && (
                <div className="chat-row">
                  <div className="chat-bubble chat-bubble-bot chat-typing" aria-label="Bot is typing">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div ref={scrollRef} className="chat-body chat-frames">
              <p className="text-muted text-xs">
                ทุกข้อความที่วิ่งผ่าน WebSocket เส้นเดียวกัน · ↑ ส่งไป server · ↓ server ส่งมา ({frames.length})
              </p>
              {frames.map((f, i) => (
                <div key={i} className={`chat-frame chat-frame-${f.dir}`}>
                  <span className="chat-frame-dir">{f.dir === "out" ? "↑" : "↓"}</span>
                  <span className="text-muted">{f.at}</span>
                  <code>{f.data}</code>
                </div>
              ))}
            </div>
          )}

          {suggestions.length > 0 && (
            <div className="chat-suggestions">
              {suggestions.map((s) => (
                <button
                  key={s}
                  type="button"
                  className="chip-toggle"
                  disabled={status !== "open" || busy}
                  onClick={() => ask(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          )}

          <form onSubmit={submit} className="chat-input-row">
            <input
              ref={inputRef}
              className="input"
              placeholder={status === "open" ? "พิมพ์ถามเรื่องสินค้า ราคา หมวดหมู่…" : "กำลังเชื่อมต่อ…"}
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              disabled={status !== "open"}
              maxLength={500}
            />
            <button
              type="submit"
              className="chat-send"
              disabled={status !== "open" || busy || !draft.trim()}
              aria-label="Send"
            >
              <SendIcon />
            </button>
          </form>
        </section>
      )}

      {showTeaser && !open && (
        <div className="chat-teaser">
          <button type="button" className="chat-teaser-text" onClick={() => toggle(true)}>
            สวัสดีครับ 👋 <strong>มีอะไรให้ช่วยมั้ย?</strong>
          </button>
          <button
            type="button"
            className="chat-teaser-close"
            onClick={() => setShowTeaser(false)}
            aria-label="Dismiss"
          >
            ×
          </button>
        </div>
      )}

      <button
        type="button"
        className={open ? "chat-fab open" : "chat-fab"}
        onClick={() => toggle(!open)}
        aria-label={open ? "Close chat" : "Open chat"}
      >
        {open ? <CloseIcon /> : <ChatIcon />}
        {!open && unread > 0 && <span className="chat-unread">{unread}</span>}
        {!open && status === "open" && <span className="chat-fab-live" />}
      </button>
    </div>
  );
}
