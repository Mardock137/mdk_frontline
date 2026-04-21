-- Migration 003: users
-- Dashboard users linked to a company. Kept minimal for the MVP and
-- prepared for future use (multi-user per company is post-MVP).

create table if not exists public.users (
    id uuid primary key default gen_random_uuid(),
    company_id uuid not null references public.companies (id) on delete cascade,
    email text not null,
    role text not null default 'owner',
    created_at timestamptz not null default now(),
    unique (company_id, email)
);

create index if not exists users_company_id_idx on public.users (company_id);

alter table public.users enable row level security;
