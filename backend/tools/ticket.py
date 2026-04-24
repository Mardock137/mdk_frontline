"""Ticket creation tool for the support agent.

Exposes:
- ``TOOL_DEFINITION``: the Anthropic-format tool schema passed to Claude.
- ``create_ticket``: the callable executed when Claude picks this tool.
"""

from __future__ import annotations

from uuid import UUID

from supabase import Client

TOOL_DEFINITION: dict = {
    "name": "create_ticket",
    "description": (
        "Crea un ticket di supporto per problemi che non possono essere risolti "
        "immediatamente tramite la knowledge base e che richiedono attenzione umana, "
        "ma senza urgenza immediata. Non usare per casi urgenti: in quel caso usa "
        "il tool 'escalate'."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "description": "Titolo breve e descrittivo del problema.",
            },
            "description": {
                "type": "string",
                "description": "Descrizione dettagliata del problema riportato dal cliente.",
            },
        },
        "required": ["subject", "description"],
    },
}


def create_ticket(
    subject: str,
    description: str,
    company_id: UUID,
    conversation_id: UUID,
    supabase: Client,
) -> str:
    """Insert a new support ticket in the database.

    Args:
        subject: Short title for the ticket.
        description: Detailed description of the issue.
        company_id: Tenant identifier.
        conversation_id: Conversation this ticket is linked to.
        supabase: Supabase client instance.

    Returns:
        A confirmation string with the new ticket ID.
    """
    row = {
        "company_id": str(company_id),
        "conversation_id": str(conversation_id),
        "subject": subject,
        "description": description,
        "status": "open",
        "is_escalation": False,
    }
    result = supabase.table("tickets").insert(row).execute()
    ticket_id = result.data[0]["id"] if result.data else "unknown"
    return f"Ticket di supporto creato con ID: {ticket_id}"
