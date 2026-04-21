-- Migration 007: messages
-- Individual messages belonging to a conversation.

create table if not exists public.messages (
    id uuid primary key default gen_random_uuid(),
    conversation_id uuid not null references public.conversations (id) on delete cascade,
    role text not null check (role in ('customer', 'agent', 'system')),
    content text not null,
    created_at timestamptz not null default now()
);

create index if not exists messages_conversation_id_idx on public.messages (conversation_id);

alter table public.messages enable row level security;
