import { readSessionToken } from "@/lib/session";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function withAuthHeaders(init?: HeadersInit): Headers {
  const headers = new Headers(init);
  const token = readSessionToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  return headers;
}

// ---------------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------------

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    const detail =
      (error as { detail?: string })?.detail ?? `Request failed (${res.status})`;
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Chat types
// ---------------------------------------------------------------------------

export interface ChatConfig {
  agent_name: string;
  company_display_name: string;
  logo_url: string | null;
  primary_color: string;
  welcome_message: string;
}

export interface SendMessageRequest {
  conversation_id: string | null;
  content: string;
}

export interface SendMessageResponse {
  conversation_id: string;
  reply: string;
}

export interface ChatMessage {
  id: string;
  role: "customer" | "agent";
  content: string;
}

// ---------------------------------------------------------------------------
// Dashboard types
// ---------------------------------------------------------------------------

export type TicketStatus = "open" | "in_progress" | "closed";

export interface Ticket {
  id: string;
  conversation_id: string;
  subject: string;
  description: string;
  status: TicketStatus;
  is_escalation: boolean;
  created_at: string;
  updated_at: string;
}

export interface AgentConfig {
  agent_name: string;
  company_display_name: string;
  primary_color: string;
  tone: "formal" | "informal";
  default_language: string;
  welcome_message: string;
}

export interface AgentConfigUpdate {
  agent_name?: string;
  company_display_name?: string;
  primary_color?: string;
  tone?: "formal" | "informal";
  default_language?: string;
  welcome_message?: string;
}

export interface TicketsByStatus {
  open: number;
  in_progress: number;
  closed: number;
}

export interface Stats {
  total_conversations: number;
  tickets_by_status: TicketsByStatus;
  escalation_open_count: number;
}

// ---------------------------------------------------------------------------
// Documents types (re-exported from backend shape)
// ---------------------------------------------------------------------------

export interface Document {
  id: string;
  filename: string;
  content_type: string;
  status: string;
  created_at: string;
  chunk_count: number;
}

export interface UploadResponse {
  document_id: string;
  chunk_count: number;
  status: string;
}

// ---------------------------------------------------------------------------
// Chat API
// ---------------------------------------------------------------------------

export async function getConfig(
  slug: string,
  signal?: AbortSignal,
): Promise<ChatConfig> {
  const res = await fetch(`${API_URL}/chat/${slug}/config`, { signal });
  return handleResponse<ChatConfig>(res);
}

export async function sendMessage(
  slug: string,
  payload: SendMessageRequest,
): Promise<SendMessageResponse> {
  const res = await fetch(`${API_URL}/chat/${slug}/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<SendMessageResponse>(res);
}

export async function getConversationMessages(
  slug: string,
  conversationId: string,
  signal?: AbortSignal,
): Promise<ChatMessage[]> {
  const res = await fetch(
    `${API_URL}/chat/${slug}/conversation/${conversationId}/messages`,
    { signal },
  );
  return handleResponse<ChatMessage[]>(res);
}

// ---------------------------------------------------------------------------
// Documents API
// ---------------------------------------------------------------------------

export async function getDocuments(): Promise<Document[]> {
  const res = await fetch(`${API_URL}/documents`, {
    headers: withAuthHeaders(),
  });
  return handleResponse<Document[]>(res);
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_URL}/documents/upload`, {
    method: "POST",
    headers: withAuthHeaders(),
    body: form,
  });
  return handleResponse<UploadResponse>(res);
}

export async function deleteDocument(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/documents/${id}`, {
    method: "DELETE",
    headers: withAuthHeaders(),
  });
  if (!res.ok && res.status !== 204) {
    const error = await res.json().catch(() => ({}));
    throw new Error((error as { detail?: string })?.detail ?? `Delete failed (${res.status})`);
  }
}

// ---------------------------------------------------------------------------
// Dashboard — Tickets API
// ---------------------------------------------------------------------------

export async function getTickets(): Promise<Ticket[]> {
  const res = await fetch(`${API_URL}/dashboard/tickets`, {
    headers: withAuthHeaders(),
  });
  return handleResponse<Ticket[]>(res);
}

export async function updateTicketStatus(id: string, status: TicketStatus): Promise<Ticket> {
  const res = await fetch(`${API_URL}/dashboard/tickets/${id}`, {
    method: "PATCH",
    headers: withAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ status }),
  });
  return handleResponse<Ticket>(res);
}

// ---------------------------------------------------------------------------
// Dashboard — Agent Config API
// ---------------------------------------------------------------------------

export async function getAgentConfig(): Promise<AgentConfig> {
  const res = await fetch(`${API_URL}/dashboard/agent-config`, {
    headers: withAuthHeaders(),
  });
  return handleResponse<AgentConfig>(res);
}

export async function updateAgentConfig(data: AgentConfigUpdate): Promise<AgentConfig> {
  const res = await fetch(`${API_URL}/dashboard/agent-config`, {
    method: "PATCH",
    headers: withAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(data),
  });
  return handleResponse<AgentConfig>(res);
}

// ---------------------------------------------------------------------------
// Dashboard — Stats API
// ---------------------------------------------------------------------------

export async function getStats(): Promise<Stats> {
  const res = await fetch(`${API_URL}/dashboard/stats`, {
    headers: withAuthHeaders(),
  });
  return handleResponse<Stats>(res);
}
