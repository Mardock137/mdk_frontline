-- Migration 016: fix Security Advisor warning "role mutable search_path"
-- Both functions relied on the caller's search_path to resolve object names.
-- Pinning search_path prevents a malicious search_path from redirecting
-- name resolution to attacker-controlled objects.

alter function frontline.set_updated_at() set search_path = frontline, pg_temp;

-- public is kept in the search_path so the vector similarity operator (<=>),
-- which lives in the vector extension in public, still resolves (phase 1).
alter function frontline.match_document_chunks(vector, uuid, integer) set search_path = frontline, public, pg_temp;
