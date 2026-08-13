const TOKEN_KEY = "groundly_admin_token";

/** Prefer absolute API URL in prod; otherwise use Vite `/api` proxy. */
function apiRoot(): string {
  const base = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "");
  return base ? base : "/api";
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers || {});
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${apiRoot()}${path}`, { ...init, headers });
  if (res.status === 204) return undefined as T;

  const text = await res.text();
  let data: unknown = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!res.ok) {
    const detail =
      typeof data === "object" && data && "detail" in data
        ? String((data as { detail: unknown }).detail)
        : text || res.statusText;
    if (res.status === 401) clearToken();
    throw new ApiError(res.status, detail);
  }
  return data as T;
}

export const api = {
  login: (email: string, password: string) =>
    request<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  me: () => request<import("../types").MeResponse>("/auth/me"),
  documents: {
    list: () => request<import("../types").Document[]>("/documents"),
    upload: (file: File) => {
      const fd = new FormData();
      fd.append("file", file);
      return request<import("../types").Document>("/documents/upload", { method: "POST", body: fd });
    },
    faq: (payload: { question: string; answer: string; title?: string }) =>
      request<import("../types").Document>("/documents/faq", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    content: (id: string) =>
      request<import("../types").DocumentContent>(`/documents/${id}/content`),
    update: (id: string, body: { source_name?: string; question?: string; answer?: string }) =>
      request<import("../types").Document>(`/documents/${id}`, {
        method: "PATCH",
        body: JSON.stringify(body),
      }),
    replacePdf: (id: string, file: File) => {
      const fd = new FormData();
      fd.append("file", file);
      return request<import("../types").Document>(`/documents/${id}/file`, {
        method: "PUT",
        body: fd,
      });
    },
    remove: (id: string) => request<void>(`/documents/${id}`, { method: "DELETE" }),
  },
  conversations: {
    list: () => request<import("../types").ConversationListItem[]>("/conversations"),
    get: (id: string) => request<import("../types").ConversationDetail>(`/conversations/${id}`),
  },
  leads: {
    list: () => request<import("../types").Lead[]>("/leads"),
    updateStatus: (id: string, status: "new" | "contacted") =>
      request<import("../types").Lead>(`/leads/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      }),
  },
  settings: {
    get: (reveal = false) =>
      request<import("../types").Settings>(`/settings?reveal_key=${reveal ? "true" : "false"}`),
    update: (body: Record<string, unknown>) =>
      request<import("../types").Settings>("/settings", {
        method: "PATCH",
        body: JSON.stringify(body),
      }),
  },
  analytics: {
    overview: () => request<import("../types").AnalyticsOverview>("/analytics/overview"),
    unanswered: () =>
      request<{ conversation_id: string; question: string; created_at: string }[]>(
        "/analytics/unanswered"
      ),
  },
};
