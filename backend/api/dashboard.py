"""Dashboard endpoints for the company admin area.

Tickets (read + status update), agent configuration (read + update), and stats.
The tenant is identified by ``DEV_COMPANY_ID`` from settings (same pattern as
``api/documents.py``).  Real authentication will replace this once the
MDK-137 integration lands.
"""

from __future__ import annotations

import logging
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from database.models import AgentTone, TicketStatus
from database.supabase_client import get_supabase_client
from utils.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _current_company_id() -> UUID:
    settings = get_settings()
    if not settings.DEV_COMPANY_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DEV_COMPANY_ID is not set",
        )
    try:
        return UUID(settings.DEV_COMPANY_ID)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DEV_COMPANY_ID is not a valid UUID",
        ) from exc


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class TicketOut(BaseModel):
    id: UUID
    conversation_id: UUID
    subject: str
    description: str
    status: TicketStatus
    is_escalation: bool
    created_at: str
    updated_at: str


class TicketStatusUpdate(BaseModel):
    status: Literal["open", "in_progress", "closed"]


class AgentConfigOut(BaseModel):
    agent_name: str
    company_display_name: str
    primary_color: str
    tone: AgentTone
    default_language: str
    welcome_message: str


class AgentConfigUpdate(BaseModel):
    agent_name: str | None = Field(default=None, min_length=1)
    company_display_name: str | None = Field(default=None, min_length=1)
    primary_color: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")
    tone: AgentTone | None = None
    default_language: str | None = Field(default=None, min_length=2, max_length=8)
    welcome_message: str | None = Field(default=None, min_length=1)


class TicketsByStatus(BaseModel):
    open: int
    in_progress: int
    closed: int


class StatsOut(BaseModel):
    total_conversations: int
    tickets_by_status: TicketsByStatus
    escalation_open_count: int


# ---------------------------------------------------------------------------
# Tickets endpoints
# ---------------------------------------------------------------------------


@router.get("/tickets", response_model=list[TicketOut])
async def list_tickets() -> list[TicketOut]:
    """Return all tickets for the current company, newest first."""
    company_id = _current_company_id()
    supabase = get_supabase_client()

    response = (
        supabase.table("tickets")
        .select(
            "id, conversation_id, subject, description, status, is_escalation,"
            " created_at, updated_at"
        )
        .eq("company_id", str(company_id))
        .order("created_at", desc=True)
        .execute()
    )
    return [TicketOut(**row) for row in (response.data or [])]


@router.patch("/tickets/{ticket_id}", response_model=TicketOut)
async def update_ticket_status(
    ticket_id: UUID,
    body: TicketStatusUpdate,
) -> TicketOut:
    """Update the status of a ticket (open → in_progress → closed)."""
    company_id = _current_company_id()
    supabase = get_supabase_client()

    existing = (
        supabase.table("tickets")
        .select("company_id")
        .eq("id", str(ticket_id))
        .limit(1)
        .execute()
    )
    rows = existing.data or []
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    if rows[0]["company_id"] != str(company_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    updated = (
        supabase.table("tickets")
        .update({"status": body.status})
        .eq("id", str(ticket_id))
        .execute()
    )
    if not updated.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update ticket",
        )

    return TicketOut(**updated.data[0])


# ---------------------------------------------------------------------------
# Agent config endpoints
# ---------------------------------------------------------------------------


@router.get("/agent-config", response_model=AgentConfigOut)
async def get_agent_config() -> AgentConfigOut:
    """Return the agent configuration for the current company."""
    company_id = _current_company_id()
    supabase = get_supabase_client()

    response = (
        supabase.table("agent_configs")
        .select(
            "agent_name, company_display_name, primary_color, tone,"
            " default_language, welcome_message"
        )
        .eq("company_id", str(company_id))
        .limit(1)
        .execute()
    )
    rows = response.data or []
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent config not found for this company",
        )
    return AgentConfigOut(**rows[0])


@router.patch("/agent-config", response_model=AgentConfigOut)
async def update_agent_config(body: AgentConfigUpdate) -> AgentConfigOut:
    """Partially update the agent configuration for the current company.

    Only the fields present in the request body are changed; omitted fields
    are left untouched.
    """
    company_id = _current_company_id()
    supabase = get_supabase_client()

    patch = body.model_dump(exclude_none=True)
    if not patch:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="No fields to update",
        )

    # tone is an enum — serialise to its string value for Supabase
    if "tone" in patch and isinstance(patch["tone"], AgentTone):
        patch["tone"] = patch["tone"].value

    updated = (
        supabase.table("agent_configs")
        .update(patch)
        .eq("company_id", str(company_id))
        .execute()
    )
    if not updated.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent config not found for this company",
        )
    return AgentConfigOut(**updated.data[0])


# ---------------------------------------------------------------------------
# Stats endpoint
# ---------------------------------------------------------------------------


@router.get("/stats", response_model=StatsOut)
async def get_stats() -> StatsOut:
    """Return dashboard statistics for the current company.

    Returns:
        - ``total_conversations``: total conversations ever started.
        - ``tickets_by_status``: ticket counts grouped by status.
        - ``escalation_open_count``: open/in-progress escalation tickets.
    """
    company_id = _current_company_id()
    supabase = get_supabase_client()

    conv_response = (
        supabase.table("conversations")
        .select("id", count="exact")
        .eq("company_id", str(company_id))
        .execute()
    )
    total_conversations: int = conv_response.count or 0

    open_response = (
        supabase.table("tickets")
        .select("id", count="exact")
        .eq("company_id", str(company_id))
        .eq("status", TicketStatus.OPEN.value)
        .execute()
    )
    open_count: int = open_response.count or 0

    in_progress_response = (
        supabase.table("tickets")
        .select("id", count="exact")
        .eq("company_id", str(company_id))
        .eq("status", TicketStatus.IN_PROGRESS.value)
        .execute()
    )
    in_progress_count: int = in_progress_response.count or 0

    closed_response = (
        supabase.table("tickets")
        .select("id", count="exact")
        .eq("company_id", str(company_id))
        .eq("status", TicketStatus.CLOSED.value)
        .execute()
    )
    closed_count: int = closed_response.count or 0

    escalation_open_response = (
        supabase.table("tickets")
        .select("id", count="exact")
        .eq("company_id", str(company_id))
        .eq("is_escalation", True)
        .neq("status", TicketStatus.CLOSED.value)
        .execute()
    )
    escalation_open_count: int = escalation_open_response.count or 0

    return StatsOut(
        total_conversations=total_conversations,
        tickets_by_status=TicketsByStatus(
            open=open_count,
            in_progress=in_progress_count,
            closed=closed_count,
        ),
        escalation_open_count=escalation_open_count,
    )
