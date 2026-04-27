"use client";

import { useEffect, useRef, useState } from "react";
import { use } from "react";
import Image from "next/image";
import { getConfig, sendMessage, type ChatConfig } from "@/lib/api";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { MessageInput } from "@/components/chat/MessageInput";
import { type Message } from "@/components/chat/MessageBubble";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeId() {
  return crypto.randomUUID();
}

function agentMessage(content: string): Message {
  return { id: makeId(), role: "agent", content };
}

function customerMessage(content: string): Message {
  return { id: makeId(), role: "customer", content };
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

interface PageProps {
  params: Promise<{ slug: string }>;
}

export default function ChatPage({ params }: PageProps) {
  const { slug } = use(params);

  const [config, setConfig] = useState<ChatConfig | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const conversationId = useRef<string | null>(null);

  // Load config on mount -------------------------------------------------
  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();

    getConfig(slug, controller.signal)
      .then((cfg) => {
        if (cancelled) return;
        setConfig(cfg);
        setMessages([agentMessage(cfg.welcome_message)]);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        if (err instanceof Error && err.name === "AbortError") return;
        const msg = err instanceof Error ? err.message : "Errore sconosciuto";
        setError(msg);
      });

    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [slug]);

  // Send message handler -------------------------------------------------
  async function handleSend(text: string) {
    if (!config) return;

    setMessages((prev) => [...prev, customerMessage(text)]);
    setIsTyping(true);

    try {
      const res = await sendMessage(slug, {
        conversation_id: conversationId.current,
        content: text,
      });

      conversationId.current = res.conversation_id;
      setMessages((prev) => [...prev, agentMessage(res.reply)]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Errore sconosciuto";
      setMessages((prev) => [
        ...prev,
        agentMessage(`Si è verificato un errore: ${msg}`),
      ]);
    } finally {
      setIsTyping(false);
    }
  }

  // Render: error state --------------------------------------------------
  if (error) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-50 p-6">
        <div className="rounded-2xl bg-white p-8 text-center shadow ring-1 ring-gray-200">
          <p className="text-lg font-semibold text-gray-800">Chat not found</p>
          <p className="mt-2 text-sm text-gray-500">{error}</p>
        </div>
      </main>
    );
  }

  // Render: loading state ------------------------------------------------
  if (!config) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-gray-700" />
      </main>
    );
  }

  const primaryColor = config.primary_color || "#000000";

  // Render: chat ---------------------------------------------------------
  return (
    <main className="flex h-screen flex-col overflow-hidden">
      {/* Header */}
      <header
        className="flex flex-shrink-0 items-center gap-3 px-6 py-4 shadow-sm"
        style={{ backgroundColor: primaryColor }}
      >
        {config.logo_url ? (
          <Image
            src={config.logo_url}
            alt={config.company_display_name}
            width={36}
            height={36}
            className="rounded-full object-cover"
          />
        ) : (
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/20 text-sm font-bold text-white">
            {config.company_display_name.charAt(0).toUpperCase()}
          </div>
        )}
        <div>
          <p className="text-sm font-semibold leading-tight text-white">
            {config.agent_name}
          </p>
          <p className="text-xs leading-tight text-white/75">
            {config.company_display_name}
          </p>
        </div>
      </header>

      {/* Messages */}
      <ChatWindow
        messages={messages}
        isTyping={isTyping}
        primaryColor={primaryColor}
      />

      {/* Input */}
      <MessageInput
        onSend={handleSend}
        disabled={isTyping}
        primaryColor={primaryColor}
      />
    </main>
  );
}
