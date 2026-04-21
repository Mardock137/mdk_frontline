-- Migration 002: companies
-- Client companies (tenants) that purchase MDK Frontline.

create table if not exists public.companies (
    id uuid primary key default gen_random_uuid(),
    slug text not null unique,
    name text not null,
    created_at timestamptz not null default now()
);

alter table public.companies enable row level security;

-- MVP: the backend uses the Supabase service role key which bypasses RLS.
-- No anon/authenticated policies are defined yet; real auth will be added
-- when MDK-137 auth integration lands (post-MVP).
