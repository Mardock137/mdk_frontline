-- Migration 008: tickets
-- Tickets opened by the agent for cases that cannot be resolved autonomously
-- or that require escalation to the company's human referent.

create table if not exists public.tickets (
    id uuid primary key default gen_random_uuid(),
    company_id uuid not null references public.companies (id) on delete cascade,
    conversation_id uuid not null references public.conversations (id) on delete cascade,
    subject text not null,
    description text not null,
    status text not null default 'open'
        check (status in ('open', 'in_progress', 'closed')),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create trigger trg_tickets_updated_at
    before update on public.tickets
    for each row execute function public.set_updated_at();

create index if not exists tickets_company_id_idx on public.tickets (company_id);
create index if not exists tickets_conversation_id_idx on public.tickets (conversation_id);
create index if not exists tickets_status_idx on public.tickets (status);

alter table public.tickets enable row level security;
