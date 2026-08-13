import { fetchConfig, streamChat, submitHandoff, type ChatFinal, type WidgetConfig } from "./api";
import { renderMarkdown } from "./markdown";
import { MARK_SVG, widgetStyles } from "./styles";

const VISITOR_KEY = "groundly_visitor_id";

export type MountOptions = {
  apiBaseUrl: string;
  apiKey: string;
  botName?: string;
  primaryColor?: string;
  welcomeMessage?: string;
  starterQuestions?: string[];
};

function uid(): string {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `v_${Math.random().toString(36).slice(2)}_${Date.now()}`;
}

function getVisitorId(): string {
  try {
    const existing = localStorage.getItem(VISITOR_KEY);
    if (existing) return existing;
    const id = uid();
    localStorage.setItem(VISITOR_KEY, id);
    return id;
  } catch {
    return uid();
  }
}

export class GroundlyChat {
  private host: HTMLElement;
  private shadow: ShadowRoot;
  private options: MountOptions;
  private config: WidgetConfig | null = null;
  private open = false;
  private busy = false;
  private conversationId: string | null = null;
  private visitorId = getVisitorId();
  private lastQuestion = "";

  private panel!: HTMLElement;
  private messagesEl!: HTMLElement;
  private input!: HTMLTextAreaElement;
  private sendBtn!: HTMLButtonElement;

  constructor(options: MountOptions) {
    this.options = options;
    this.host = document.createElement("div");
    this.host.id = "groundly-widget-host";
    document.body.appendChild(this.host);
    this.shadow = this.host.attachShadow({ mode: "open" });
    void this.init();
  }

  private async init() {
    let primary = this.options.primaryColor || "#0F766E";
    let botName = this.options.botName || "Support Assistant";
    let welcome = this.options.welcomeMessage || "Hi! Ask me anything.";
    let starters = this.options.starterQuestions || [];

    try {
      this.config = await fetchConfig(this.options.apiBaseUrl, this.options.apiKey);
      primary = this.config.primary_color || primary;
      botName = this.config.bot_name || botName;
      welcome = this.config.welcome_message || welcome;
      starters = this.config.starter_questions?.length
        ? this.config.starter_questions
        : starters;
    } catch {
      // Config optional if embed attributes provide branding
    }

    const style = document.createElement("style");
    style.textContent = widgetStyles(primary);
    this.shadow.appendChild(style);

    // Load fonts into document (shadow can't load document fonts alone easily)
    this.ensureFonts();

    const root = document.createElement("div");
    root.className = "gw-root";
    root.innerHTML = `
      <div class="gw-panel" part="panel" role="dialog" aria-label="${escapeAttr(botName)}">
        <div class="gw-header">
          <div class="gw-header-left">
            <div class="gw-avatar">${MARK_SVG}</div>
            <div>
              <div class="gw-title">${escapeHtml(botName)}</div>
              <div class="gw-sub">Grounded answers</div>
            </div>
          </div>
          <button type="button" class="gw-close" aria-label="Close">×</button>
        </div>
        <div class="gw-messages"></div>
        <div class="gw-composer">
          <form class="gw-form">
            <textarea class="gw-input" rows="1" placeholder="Ask a question…" aria-label="Message"></textarea>
            <button class="gw-send" type="submit" aria-label="Send">↑</button>
          </form>
          <div class="gw-privacy">Ask about hours, insurance, or appointments</div>
        </div>
      </div>
      <button type="button" class="gw-launcher" aria-label="Open chat">${MARK_SVG}</button>
    `;
    this.shadow.appendChild(root);

    this.panel = root.querySelector(".gw-panel") as HTMLElement;
    this.messagesEl = root.querySelector(".gw-messages") as HTMLElement;
    this.input = root.querySelector(".gw-input") as HTMLTextAreaElement;
    this.sendBtn = root.querySelector(".gw-send") as HTMLButtonElement;
    const launcher = root.querySelector(".gw-launcher") as HTMLButtonElement;
    const closeBtn = root.querySelector(".gw-close") as HTMLButtonElement;
    const form = root.querySelector(".gw-form") as HTMLFormElement;

    launcher.addEventListener("click", () => this.setOpen(!this.open));
    closeBtn.addEventListener("click", () => this.setOpen(false));
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      void this.send(this.input.value);
    });
    this.input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        void this.send(this.input.value);
      }
    });

    this.addAssistant(welcome);
    if (starters.length) {
      this.renderStarters(starters);
    }
  }

  private ensureFonts() {
    const id = "groundly-fonts";
    if (document.getElementById(id)) return;
    const link = document.createElement("link");
    link.id = id;
    link.rel = "stylesheet";
    link.href =
      "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap";
    document.head.appendChild(link);
  }

  private setOpen(next: boolean) {
    this.open = next;
    this.panel.classList.toggle("open", next);
    if (next) {
      this.input.focus();
    }
  }

  private renderStarters(starters: string[]) {
    const wrap = document.createElement("div");
    wrap.className = "gw-starters";
    for (const q of starters) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "gw-starter";
      btn.textContent = q;
      btn.addEventListener("click", () => void this.send(q));
      wrap.appendChild(btn);
    }
    this.messagesEl.appendChild(wrap);
  }

  private addUser(text: string) {
    const el = document.createElement("div");
    el.className = "gw-bubble user";
    el.textContent = text;
    this.messagesEl.appendChild(el);
    this.scrollBottom();
  }

  private addAssistant(text: string) {
    const el = document.createElement("div");
    el.className = "gw-bubble assistant";
    el.innerHTML = renderMarkdown(text);
    this.messagesEl.appendChild(el);
    this.scrollBottom();
    return el;
  }

  private showTyping() {
    const el = document.createElement("div");
    el.className = "gw-typing";
    el.innerHTML = "<span></span><span></span><span></span>";
    this.messagesEl.appendChild(el);
    this.scrollBottom();
    return el;
  }

  private scrollBottom() {
    this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
  }

  private async send(raw: string) {
    const message = raw.trim();
    if (!message || this.busy) return;
    this.busy = true;
    this.lastQuestion = message;
    this.input.value = "";
    this.sendBtn.disabled = true;

    // remove starters after first question
    this.messagesEl.querySelector(".gw-starters")?.remove();

    this.addUser(message);
    const typing = this.showTyping();
    let bubble: HTMLElement | null = null;
    let assembled = "";

    try {
      const final = await streamChat({
        apiBase: this.options.apiBaseUrl,
        apiKey: this.options.apiKey,
        visitorId: this.visitorId,
        conversationId: this.conversationId,
        message,
        onToken: (text) => {
          if (!bubble) {
            typing.remove();
            bubble = this.addAssistant("");
          }
          assembled += text;
          bubble.innerHTML = renderMarkdown(assembled);
          this.scrollBottom();
        },
      });

      this.conversationId = final.conversation_id;
      typing.remove();
      if (!bubble) {
        bubble = this.addAssistant(final.answer);
      } else {
        bubble.innerHTML = renderMarkdown(final.answer);
      }

      if (final.was_fallback) {
        this.showLeadForm(final.conversation_id);
      }
    } catch (err) {
      typing.remove();
      const msg = err instanceof Error ? err.message : "Something went wrong";
      this.addAssistant(`Sorry — ${msg}`);
    } finally {
      this.busy = false;
      this.sendBtn.disabled = false;
      this.input.focus();
    }
  }

  private showLeadForm(conversationId: string) {
    const box = document.createElement("div");
    box.className = "gw-lead";
    box.innerHTML = `
      <h4>Connect with the team</h4>
      <p>I’m not sure about that. Leave your details and someone will follow up.</p>
      <input type="email" name="email" placeholder="Email *" required />
      <input type="text" name="name" placeholder="Name (optional)" />
      <input type="tel" name="phone" placeholder="Phone (optional)" />
      <div class="gw-lead-actions">
        <button type="button" class="gw-btn primary">Send</button>
        <button type="button" class="gw-btn ghost">Dismiss</button>
      </div>
    `;
    const email = box.querySelector('input[name="email"]') as HTMLInputElement;
    const name = box.querySelector('input[name="name"]') as HTMLInputElement;
    const phone = box.querySelector('input[name="phone"]') as HTMLInputElement;
    const send = box.querySelector(".gw-btn.primary") as HTMLButtonElement;
    const dismiss = box.querySelector(".gw-btn.ghost") as HTMLButtonElement;

    dismiss.addEventListener("click", () => box.remove());
    send.addEventListener("click", async () => {
      if (!email.value.trim()) {
        email.focus();
        return;
      }
      send.disabled = true;
      try {
        await submitHandoff({
          apiBase: this.options.apiBaseUrl,
          apiKey: this.options.apiKey,
          conversationId,
          visitorId: this.visitorId,
          email: email.value.trim(),
          name: name.value.trim() || undefined,
          phone: phone.value.trim() || undefined,
          question: this.lastQuestion,
        });
        box.innerHTML = `<h4>Thanks</h4><p>Your note is with the team. We’ll be in touch.</p>`;
      } catch (err) {
        send.disabled = false;
        const msg = err instanceof Error ? err.message : "Failed";
        box.querySelector("p")!.textContent = msg;
      }
    });

    this.messagesEl.appendChild(box);
    this.scrollBottom();
  }
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escapeAttr(s: string): string {
  return escapeHtml(s).replace(/'/g, "&#39;");
}

export function mountGroundlyWidget(options: MountOptions): GroundlyChat {
  return new GroundlyChat(options);
}
