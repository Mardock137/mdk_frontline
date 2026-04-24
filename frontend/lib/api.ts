const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Types
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

// ---------------------------------------------------------------------------
// API calls
// ---------------------------------------------------------------------------

/**
 * Fetches branding and welcome message for the given company slug.
 * Throws if the company is not found (404) or on network errors.
 */
export async function getConfig(slug: string): Promise<ChatConfig> {
  const res = await fetch(`${API_URL}/chat/${slug}/config`);

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error?.detail ?? `Failed to load config (${res.status})`);
  }

  return res.json() as Promise<ChatConfig>;
}

/**
 * Sends a customer message to the AI agent.
 * Pass `conversation_id: null` to start a new conversation.
 * Returns the agent reply and the conversation_id to reuse for subsequent messages.
 */
export async function sendMessage(
  slug: string,
  payload: SendMessageRequest,
): Promise<SendMessageResponse> {
  const res = await fetch(`${API_URL}/chat/${slug}/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error?.detail ?? `Request failed (${res.status})`);
  }

  return res.json() as Promise<SendMessageResponse>;
}
