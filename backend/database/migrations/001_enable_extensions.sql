-- Migration 001: Enable required PostgreSQL extensions.
-- pgvector is used in phase 3 for semantic search on the knowledge base.

create extension if not exists "vector";
create extension if not exists "pgcrypto";
