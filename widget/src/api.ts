export type WidgetConfig = {
  bot_name: string;
  primary_color: string;
  welcome_message: string;
  starter_questions: string[];
  business_name: string;
};

export type Citation = {
  chunk_id: string;
  document: string;
  excerpt: string;
  page?: number | null;
};

export type ChatFinal = {
  conversation_id: string;
  answer: string;
  citations: Citation[];
  was_fallback: boolean;
};

function headers(apiKey: string, extra?: HeadersInit): HeadersInit {
  return {
    "Content-Type": "application/json",
    "X-Api-Key": apiKey,
    ...(extra || {}),
  };
}

export async function fetchConfig(apiBase: string, apiKey: string): Promise<WidgetConfig> {
  const res = await fetch(`${apiBase.replace(/\/$/, "")}/widget/config`, {
    headers: headers(apiKey),
  });
  if (!res.ok) {
    throw new Error(`Config failed (${res.status})`);
  }
  return res.json();
}

export async function streamChat(options: {
  apiBase: string;
  apiKey: string;
  visitorId: string;
  conversationId: string | null;
  message: string;
  onToken: (text: string) => void;
}): Promise<ChatFinal> {
  const res = await fetch(`${options.apiBase.replace(/\/$/, "")}/chat/message/stream`, {
    method: "POST",
    headers: headers(options.apiKey),
    body: JSON.stringify({
      visitor_id: options.visitorId,
      conversation_id: options.conversationId,
      message: options.message,
    }),
  });

  if (!res.ok || !res.body) {
    const detail = await res.text();
    throw new Error(detail || `Chat failed (${res.status})`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finalPayload: ChatFinal | null = null;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const parts = buffer.split("\n\n");
    buffer = parts.pop() || "";

    for (const part of parts) {
      const lines = part.split("\n");
      let event = "message";
      let data = "";
      for (const line of lines) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        if (line.startsWith("data:")) data += line.slice(5).trim();
      }
      if (!data) continue;
      const parsed = JSON.parse(data);
      if (event === "token" && parsed.text) {
        options.onToken(parsed.text);
      } else if (event === "final") {
        finalPayload = parsed as ChatFinal;
      } else if (event === "error") {
        throw new Error(parsed.detail || "Stream error");
      }
    }
  }

  if (!finalPayload) {
    throw new Error("Stream ended without final event");
  }
  return finalPayload;
}

export async function submitHandoff(options: {
  apiBase: string;
  apiKey: string;
  conversationId: string;
  visitorId: string;
  email: string;
  name?: string;
  phone?: string;
  question: string;
}): Promise<void> {
  const res = await fetch(`${options.apiBase.replace(/\/$/, "")}/chat/handoff`, {
    method: "POST",
    headers: headers(options.apiKey),
    body: JSON.stringify({
      conversation_id: options.conversationId,
      visitor_id: options.visitorId,
      email: options.email,
      name: options.name || null,
      phone: options.phone || null,
      question: options.question,
    }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `Handoff failed (${res.status})`);
  }
}
