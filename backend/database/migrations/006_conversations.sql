-- Migration 006: conversations
-- Live chat conversations between end customers and the AI agent.

create table if not exists public.conversations (
    id uuid primary key default gen_random_uuid(),
    company_id uuid not null references public.companies (id) on delete cascade,
    status text not null default 'active'
        check (status in ('active', 'closed', 'escalated')),
    started_at timestamptz not null default now()
);

create index if not exists conversations_company_id_idx on public.conversations (company_id);
create index if not exists conversations_status_idx on public.conversations (status);

alter table public.conversations enable row level security;
