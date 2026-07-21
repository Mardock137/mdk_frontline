-- Migration 001: Enable required PostgreSQL extensions.
-- pgvector is used in phase 3 for semantic search on the knowledge base.

create extension if not exists "vector";
create extension if not exists "pgcrypto";

-- Dedicated schema for all MDK Frontline objects, so the public schema stays
-- free for a future second product. The vector extension stays in public for
-- now (moved to a dedicated schema in phase 2).
create schema if not exists frontline;
