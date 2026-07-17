-- Migration 016: fix Security Advisor warning "role mutable search_path"
-- Both functions relied on the caller's search_path to resolve object names.
-- Pinning search_path prevents a malicious search_path from redirecting
-- name resolution to attacker-controlled objects.

alter function public.set_updated_at() set search_path = public, pg_temp;

alter function public.match_document_chunks(vector, uuid, integer) set search_path = public, pg_temp;
