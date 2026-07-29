#!/usr/bin/env python3

import os

from flask import Flask, jsonify, render_template_string, request
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    def load_dotenv(*args, **kwargs):  # type: ignore[override]
        return False

from engine import ConversationEngine
from storage import Storage


LANDING_PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BRDGE RAG Learning Assistant</title>
  <style>
    :root {
      --ink: #0a1027;
      --navy: #0b1028;
      --navy-soft: #1b2356;
      --panel: rgba(9, 13, 33, 0.72);
      --panel-light: rgba(246, 247, 251, 0.96);
      --panel-border: rgba(255, 255, 255, 0.14);
      --blue: #2f63ff;
      --blue-bright: #4e77ff;
      --lavender: #dce0ef;
      --muted: #95a0c6;
      --mist: #f6f7fb;
      --white: #ffffff;
      --success: #3ddc97;
      --warning: #f7c948;
    }

    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--white);
      font-family: "Avenir Next", "Space Grotesk", "Helvetica Neue", sans-serif;
      background:
        radial-gradient(circle at 84% 12%, rgba(47, 99, 255, 0.25), transparent 30rem),
        radial-gradient(circle at 10% 88%, rgba(52, 64, 171, 0.42), transparent 26rem),
        linear-gradient(135deg, #090d21 0%, #101744 48%, #171d49 100%);
    }

    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
      padding: 1rem clamp(1.2rem, 4vw, 3rem);
      background: rgba(246, 247, 251, 0.95);
      color: var(--ink);
      position: sticky;
      top: 0;
      z-index: 20;
      backdrop-filter: blur(10px);
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 0.8rem;
      font-size: clamp(1.5rem, 2.4vw, 2.3rem);
      font-weight: 700;
      letter-spacing: -0.04em;
      color: #27328b;
    }

    .mark {
      position: relative;
      width: 1.6rem;
      height: 1.6rem;
    }

    .mark::before, .mark::after, .mark span {
      content: "";
      position: absolute;
      width: 0.7rem;
      height: 0.7rem;
      background: var(--blue);
    }

    .mark::before { top: 0; right: 0; }
    .mark span { top: 0.48rem; left: 0.18rem; }
    .mark::after { right: 0; bottom: 0; background: #2143b7; }

    .nav {
      display: flex;
      align-items: center;
      gap: clamp(0.9rem, 2.2vw, 2rem);
      color: #59617f;
      font-weight: 600;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    .pill {
      border: 0;
      border-radius: 999px;
      padding: 0.85rem 1.4rem;
      background: var(--ink);
      color: var(--white);
      font: inherit;
    }

    main {
      width: min(94rem, calc(100% - 2rem));
      margin: 0 auto;
      padding: clamp(1rem, 3vw, 2rem) 0 4rem;
    }

    .shell {
      display: grid;
      grid-template-columns: 19rem minmax(0, 1fr) 24rem;
      gap: 1rem;
      margin-top: 1rem;
    }

    .card {
      border: 1px solid rgba(255, 255, 255, 0.14);
      border-radius: 1.6rem;
      padding: 1.25rem;
      background: var(--panel);
      box-shadow: 0 24px 80px rgba(2, 5, 25, 0.28);
      backdrop-filter: blur(18px);
      min-width: 0;
    }

    .card.light {
      background: var(--panel-light);
      color: var(--ink);
    }

    .section-label {
      margin: 0 0 0.8rem;
      color: var(--blue-bright);
      font-size: 0.78rem;
      font-weight: 800;
      letter-spacing: 0.2em;
      text-transform: uppercase;
    }

    h2 {
      margin: 0 0 1rem;
      font-size: clamp(1.45rem, 2.6vw, 2.1rem);
      letter-spacing: -0.055em;
    }

    p {
      line-height: 1.6;
      margin: 0;
    }

    .muted { color: var(--muted); }
    .light .muted { color: #59617f; }

    .stack {
      display: grid;
      gap: 0.9rem;
    }

    .field {
      display: grid;
      gap: 0.45rem;
    }

    label {
      font-size: 0.83rem;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: #bac1df;
    }

    .light label { color: #5f6888; }

    input, textarea, select {
      width: 100%;
      border: 1px solid rgba(255, 255, 255, 0.14);
      border-radius: 1rem;
      padding: 0.95rem 1rem;
      background: rgba(255, 255, 255, 0.06);
      color: inherit;
      font: inherit;
      outline: none;
    }

    .light input, .light textarea, .light select {
      border-color: rgba(10, 16, 39, 0.12);
      background: rgba(255, 255, 255, 0.95);
      color: var(--ink);
    }

    textarea {
      min-height: 5.5rem;
      resize: vertical;
    }

    .button-row {
      display: flex;
      flex-wrap: wrap;
      gap: 0.65rem;
    }

    .chip {
      border: 1px solid rgba(255, 255, 255, 0.16);
      border-radius: 999px;
      padding: 0.6rem 0.85rem;
      background: rgba(255, 255, 255, 0.06);
      color: var(--white);
      font: inherit;
      cursor: pointer;
    }

    .light .chip {
      border-color: rgba(10, 16, 39, 0.12);
      background: rgba(47, 99, 255, 0.08);
      color: var(--ink);
    }

    .flow {
      display: grid;
      gap: 0.8rem;
      margin-top: 1rem;
    }

    .step {
      display: grid;
      gap: 0.4rem;
      padding-top: 0.8rem;
      border-top: 1px solid rgba(255, 255, 255, 0.12);
      color: var(--lavender);
    }

    .step strong {
      color: var(--white);
      font-size: 0.95rem;
    }

    .status-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 0.7rem;
      margin-top: 1rem;
    }

    .status-pill {
      padding: 0.8rem 0.9rem;
      border-radius: 1rem;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.12);
    }

    .status-label {
      display: block;
      font-size: 0.72rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 0.2rem;
    }

    .status-value {
      font-weight: 700;
      word-break: break-word;
    }

    .transcript {
      display: grid;
      gap: 0.85rem;
      min-height: 28rem;
      max-height: calc(100vh - 18rem);
      overflow: auto;
      padding-right: 0.35rem;
      align-content: start;
    }

    .bubble {
      max-width: 92%;
      border-radius: 1.2rem;
      padding: 0.95rem 1rem;
      line-height: 1.55;
      white-space: pre-wrap;
    }

    .bubble.assistant {
      background: rgba(255, 255, 255, 0.09);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: var(--white);
      justify-self: start;
    }

    .bubble.user {
      background: rgba(47, 99, 255, 0.18);
      border: 1px solid rgba(47, 99, 255, 0.28);
      justify-self: end;
    }

    .bubble-meta {
      display: block;
      margin-bottom: 0.35rem;
      font-size: 0.74rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
    }

    .composer {
      display: grid;
      gap: 0.8rem;
      margin-top: 1rem;
    }

    .composer-row {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 0.75rem;
      align-items: end;
    }

    .hint {
      color: #8f97b8;
      font-size: 0.92rem;
    }

    .pathway {
      display: grid;
      gap: 0.8rem;
      min-height: 28rem;
      max-height: calc(100vh - 18rem);
      overflow: auto;
      white-space: pre-wrap;
      color: #eff2ff;
    }

    .pathway.empty {
      color: #98a2c7;
    }

    .pathway code {
      display: inline-block;
      margin: 0.2rem 0;
      padding: 0.25rem 0.5rem;
      border-radius: 0.7rem;
      background: rgba(47, 99, 255, 0.12);
      color: var(--blue-bright);
      font-weight: 700;
    }

    .alert {
      display: none;
      margin-top: 0.8rem;
      padding: 0.8rem 0.95rem;
      border-radius: 1rem;
      background: rgba(247, 201, 72, 0.12);
      border: 1px solid rgba(247, 201, 72, 0.2);
      color: #fff0be;
    }

    .alert.show { display: block; }

    .tiny-label {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      color: var(--muted);
      font-size: 0.76rem;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      margin-bottom: 0.85rem;
    }

    .tiny-label::before {
      content: "";
      width: 1.3rem;
      height: 2px;
      background: var(--blue-bright);
    }

    .chat-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .chat-title h2 {
      margin: 0;
    }

    .chat-toolbar {
      display: flex;
      gap: 0.6rem;
      flex-wrap: wrap;
    }

    .ghost {
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 999px;
      padding: 0.55rem 0.9rem;
      background: rgba(255, 255, 255, 0.04);
      color: var(--white);
      font: inherit;
    }

    .composer-shell {
      position: sticky;
      bottom: 0;
      padding-top: 0.9rem;
      background: linear-gradient(180deg, rgba(11, 16, 40, 0), rgba(11, 16, 40, 0.9) 32%);
    }

    .composer-box {
      display: grid;
      gap: 0.7rem;
      padding: 0.9rem;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 1.35rem;
      background: rgba(255, 255, 255, 0.06);
    }

    .composer-row {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 0.75rem;
      align-items: end;
    }

    .composer-note {
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      color: #8f97b8;
      font-size: 0.9rem;
      flex-wrap: wrap;
    }

    .send {
      border: 0;
      border-radius: 999px;
      padding: 0 1.2rem;
      min-height: 3.25rem;
      background: var(--blue);
      color: var(--white);
      font-weight: 800;
      cursor: pointer;
    }

    .title-line {
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      align-items: center;
      margin-top: 0.4rem;
    }

    .title-line .eyebrow {
      margin: 0;
    }

    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 0.9rem;
      color: var(--blue-bright);
      font-size: 0.8rem;
      font-weight: 800;
      letter-spacing: 0.22em;
      text-transform: uppercase;
    }

    .eyebrow::before {
      content: "";
      width: 2.4rem;
      height: 2px;
      background: var(--blue-bright);
    }

    .eyebrow.small::before {
      width: 1.4rem;
    }

    .panel-head {
      display: grid;
      gap: 0.4rem;
      margin-bottom: 1rem;
    }

    @media (max-width: 1180px) {
      .shell { grid-template-columns: 1fr; }
    }

    @media (max-width: 820px) {
      .nav { display: none; }
      .composer-row { grid-template-columns: 1fr; }
      .status-grid { grid-template-columns: 1fr; }
      .bubble { max-width: 100%; }
    }
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand"><span class="mark"><span></span></span>Brdge</div>
    <nav class="nav" aria-label="Main navigation">
      <span>Home</span>
      <span>Enterprise</span>
      <span>Launchpad</span>
      <button class="pill" type="button">Get in Touch</button>
    </nav>
  </header>

  <main>
    <section class="shell" aria-label="Rai chat interface">
      <aside class="card light">
        <div class="panel-head">
          <div class="tiny-label">Sidebar</div>
          <h2>Session controls</h2>
        </div>
        <div class="stack">
          <div class="field">
            <label for="user-id">User ID</label>
            <input id="user-id" name="user-id" type="text" placeholder="demo-user">
          </div>
          <div class="button-row">
            <button id="start-new" class="chip" type="button">Start new</button>
            <button id="resume-last" class="chip" type="button">Resume last</button>
          </div>
          <p class="muted">A new user goes straight to consent. A returning user can resume or start fresh.</p>
        </div>

        <div class="flow" style="margin-top: 1.2rem;">
          <div class="step">
            <strong>Consent</strong>
            <span class="muted">Share the report, or skip it. Introductory videos remain optional for everyone.</span>
            <div class="button-row">
              <button id="consent-yes" class="chip" type="button">Share report</button>
              <button id="consent-no" class="chip" type="button">Skip report</button>
            </div>
          </div>

          <div class="step">
            <strong>Select an area</strong>
            <span class="muted">Pick one specific sub-facet, then keep the dialogue there unless you clearly switch.</span>
            <div class="button-row">
              <button class="chip area-chip" type="button" data-area="work life balance">Work-life balance</button>
              <button class="chip area-chip" type="button" data-area="adapting to change">Adapting to change</button>
              <button class="chip area-chip" type="button" data-area="managing conflict">Managing conflict</button>
              <button class="chip area-chip" type="button" data-area="procrastination">Procrastination</button>
            </div>
          </div>
        </div>

        <div class="status-grid" aria-live="polite">
          <div class="status-pill">
            <span class="status-label">Session</span>
            <span class="status-value" id="session-state">Not started</span>
          </div>
          <div class="status-pill">
            <span class="status-label">Consent</span>
            <span class="status-value" id="consent-state">Unset</span>
          </div>
          <div class="status-pill">
            <span class="status-label">Area</span>
            <span class="status-value" id="area-state">None</span>
          </div>
          <div class="status-pill">
            <span class="status-label">Turns</span>
            <span class="status-value" id="turn-state">0</span>
          </div>
        </div>

        <div class="alert" id="entry-alert"></div>
      </aside>

      <section class="card">
        <div class="panel-head">
          <div class="tiny-label">Chat</div>
          <div class="chat-title">
            <h2>Chat with Rai</h2>
            <div class="chat-toolbar">
              <button id="clear-chat" class="ghost" type="button">Clear view</button>
            </div>
          </div>
        </div>
        <div id="transcript" class="transcript" aria-live="polite" aria-label="Conversation transcript"></div>
        <div class="composer-shell" id="composer">
          <div class="composer-box">
            <div class="field">
              <label for="message">Message</label>
              <textarea id="message" placeholder="Message Rai. Enter sends. Shift+Enter makes a new line."></textarea>
            </div>
            <div class="composer-note">
              <span>Enter sends.</span>
              <span>Shift+Enter adds a new line.</span>
            </div>
            <div class="composer-row">
              <span class="hint">Use plain language. Clear intent changes the area; incidental keywords do not.</span>
              <button id="send-message" class="send" type="button">Send</button>
            </div>
          </div>
        </div>
      </section>

      <aside class="card">
        <div class="panel-head">
          <div class="tiny-label">Pathway</div>
          <h2>Current output</h2>
        </div>
        <div id="pathway" class="pathway empty">
          Start a session and work through the conversation. Once Rai generates a pathway, it will appear here in priority order:
          <code>Video</code>, <code>Slides</code>, <code>Worksheet / Exercises</code>, <code>Posts</code>.
        </div>
      </aside>
    </section>
  </main>

  <script>
    const state = {
      userId: localStorage.getItem("brdge.userId") || "demo-user",
      session: null,
      pathway: "",
      started: false,
    };

    const el = {
      userId: document.getElementById("user-id"),
      transcript: document.getElementById("transcript"),
      message: document.getElementById("message"),
      pathway: document.getElementById("pathway"),
      alert: document.getElementById("entry-alert"),
      sessionState: document.getElementById("session-state"),
      consentState: document.getElementById("consent-state"),
      areaState: document.getElementById("area-state"),
      turnState: document.getElementById("turn-state"),
      startNew: document.getElementById("start-new"),
      resumeLast: document.getElementById("resume-last"),
      consentYes: document.getElementById("consent-yes"),
      consentNo: document.getElementById("consent-no"),
      sendMessage: document.getElementById("send-message"),
      clearChat: document.getElementById("clear-chat"),
      areaChips: Array.from(document.querySelectorAll(".area-chip")),
    };

    function setAlert(text) {
      if (!text) {
        el.alert.classList.remove("show");
        el.alert.textContent = "";
        return;
      }
      el.alert.textContent = text;
      el.alert.classList.add("show");
    }

    function saveUserId(value) {
      state.userId = value.trim();
      localStorage.setItem("brdge.userId", state.userId);
      localStorage.setItem("brdge.sessionStarted", "true");
      el.userId.value = state.userId;
    }

    function renderSession() {
      const session = state.session || {};
      el.sessionState.textContent = state.started ? `Active: ${state.userId || "unknown"}` : "Not started";
      el.consentState.textContent = session.consent === true ? "Granted" : session.consent === false ? "Declined" : "Unset";
      el.areaState.textContent = session.current_subfacet_name || "None";
      el.turnState.textContent = String(session.turn_count || 0);
    }

    function addBubble(role, text) {
      const bubble = document.createElement("div");
      bubble.className = `bubble ${role}`;
      const meta = document.createElement("span");
      meta.className = "bubble-meta";
      meta.textContent = role === "assistant" ? "Rai" : "You";
      const body = document.createElement("p");
      body.textContent = text;
      bubble.append(meta, body);
      el.transcript.appendChild(bubble);
      el.transcript.scrollTop = el.transcript.scrollHeight;
    }

    function replaceTranscript(text, role = "assistant") {
      if (text) {
        addBubble(role, text);
      }
    }

    function renderPathway(text) {
      state.pathway = text || "";
      if (!text) {
        el.pathway.classList.add("empty");
        el.pathway.textContent = "Start a session and work through the conversation. Once Rai generates a pathway, it will appear here in priority order: Video, Slides, Worksheet / Exercises, Posts.";
        return;
      }
      el.pathway.classList.remove("empty");
      el.pathway.textContent = text;
    }

    async function postJSON(url, payload) {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Request failed");
      }
      return data;
    }

    function ingest(data, clearTranscript = false) {
      state.session = data.session || null;
      state.started = true;
      if (clearTranscript) {
        el.transcript.innerHTML = "";
      }
      replaceTranscript(data.reply, "assistant");
      renderSession();
      if (data.reply && data.reply.startsWith("Learning Pathway for")) {
        renderPathway(data.reply);
      }
      setAlert("");
    }

    async function startConversation(returning) {
      const userId = el.userId.value.trim();
      if (!userId) {
        setAlert("Enter a user ID first.");
        return;
      }
      saveUserId(userId);
      setAlert("");
      try {
        const payload = returning
          ? { user_id: userId, returning: true, reset: false }
          : { user_id: userId, returning: false, reset: true };
        const data = await postJSON(returning ? "/resume" : "/start", payload);
        ingest(data, true);
      } catch (error) {
        setAlert(error.message);
      }
    }

    async function sendConsent(consent) {
      const userId = el.userId.value.trim();
      if (!userId) {
        setAlert("Start or resume a session first.");
        return;
      }
      saveUserId(userId);
      try {
        const data = await postJSON("/consent", { user_id: userId, consent });
        ingest(data);
      } catch (error) {
        setAlert(error.message);
      }
    }

    async function sendMessage(text) {
      const userId = el.userId.value.trim();
      if (!userId) {
        setAlert("Start or resume a session first.");
        return;
      }
      const message = text.trim();
      if (!message) {
        setAlert("Type a message first.");
        return;
      }
      saveUserId(userId);
      addBubble("user", message);
      el.message.value = "";
      try {
        const data = await postJSON("/chat", { user_id: userId, message });
        ingest(data);
      } catch (error) {
        setAlert(error.message);
      }
    }

    el.startNew.addEventListener("click", () => startConversation(false));
    el.resumeLast.addEventListener("click", () => startConversation(true));
    el.consentYes.addEventListener("click", () => sendConsent(true));
    el.consentNo.addEventListener("click", () => sendConsent(false));
    el.sendMessage.addEventListener("click", () => sendMessage(el.message.value));
    el.message.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage(el.message.value);
      }
    });
    el.clearChat.addEventListener("click", () => {
      el.transcript.innerHTML = "";
      setAlert("Chat view cleared. The session is unchanged.");
    });
    el.userId.value = state.userId;
    if (!localStorage.getItem("brdge.sessionStarted")) {
      window.setTimeout(() => startConversation(false), 0);
    }

    el.areaChips.forEach((button) => {
      button.addEventListener("click", () => {
        const area = button.dataset.area || button.textContent.trim();
        el.message.value = `I want help with ${area}`;
        el.message.focus();
        setAlert("Area selected. Send the message to lock Rai onto that sub-facet.");
      });
    });

    renderSession();
  </script>
</body>
</html>
"""


def create_app(
    storage: Storage | None = None,
    engine: ConversationEngine | None = None,
) -> Flask:
    load_dotenv()

    app = Flask(__name__)

    app_storage = storage or Storage()
    app_storage.initialize()
    engine = engine or ConversationEngine(storage=app_storage)

    @app.get("/")
    def index() -> tuple[str, int] | tuple[dict, int]:
        routes = {
            "health": "GET /health",
            "start": "POST /start",
            "consent": "POST /consent",
            "chat": "POST /chat",
            "resume": "POST /resume",
        }
        if request.args.get("format") == "json":
            return jsonify(
                {
                    "service": "BRDGE RAG Learning Assistant",
                    "routes": routes,
                }
            ), 200
        return render_template_string(LANDING_PAGE), 200

    @app.get("/health")
    def health() -> tuple[dict[str, str], int]:
        return {"status": "ok"}, 200

    @app.post("/start")
    def start() -> tuple[dict, int]:
        payload = request.get_json(silent=True) or {}
        user_id = (payload.get("user_id") or "").strip()
        returning = bool(payload.get("returning", False))
        reset = bool(payload.get("reset", False))

        if not user_id:
            return {"error": "user_id is required"}, 400

        result = engine.start_session(user_id=user_id, returning=returning, reset=reset)
        return jsonify(
            {
                "reply": result["reply"],
                "session": result["session"],
            }
        ), 200

    @app.post("/consent")
    def consent() -> tuple[dict, int]:
        payload = request.get_json(silent=True) or {}
        user_id = (payload.get("user_id") or "").strip()
        consent_value = payload.get("consent")

        if not user_id:
            return {"error": "user_id is required"}, 400
        if not isinstance(consent_value, bool):
            return {"error": "consent must be true or false"}, 400

        result = engine.set_consent(user_id=user_id, consent=consent_value)
        return jsonify(
            {
                "reply": result["reply"],
                "session": result["session"],
            }
        ), 200

    @app.post("/chat")
    def chat() -> tuple[dict, int]:
        payload = request.get_json(silent=True) or {}
        user_id = (payload.get("user_id") or "").strip()
        message = (payload.get("message") or "").strip()

        if not user_id:
            return {"error": "user_id is required"}, 400
        if not message:
            return {"error": "message is required"}, 400

        result = engine.handle_user_message(user_id=user_id, text=message)
        return jsonify(
            {
                "reply": result["reply"],
                "session": result["session"],
            }
        ), 200

    @app.post("/resume")
    def resume() -> tuple[dict, int]:
        payload = request.get_json(silent=True) or {}
        user_id = (payload.get("user_id") or "").strip()

        if not user_id:
            return {"error": "user_id is required"}, 400

        result = engine.start_session(user_id=user_id, returning=True)
        return jsonify(
            {
                "reply": result["reply"],
                "session": result["session"],
            }
        ), 200

    return app


app = create_app()


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)
