"""Escalation tool for the support agent.

Exposes:
- ``TOOL_DEFINITION``: the Anthropic-format tool schema passed to Claude.
- ``escalate``: the callable executed when Claude picks this tool.
"""

from __future__ import annotations

import logging
from uuid import UUID

from supabase import Client

logger = logging.getLogger(__name__)

TOOL_DEFINITION: dict = {
    "name": "escalate",
    "description": (
        "Escala la conversazione a un operatore umano quando il problema è urgente, "
        "complesso, o richiede un intervento diretto del team aziendale. "
        "Usare solo quando il problema non può essere gestito autonomamente e "
        "richiede attenzione immediata."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "description": "Titolo breve e descrittivo del motivo dell'escalation.",
            },
            "description": {
                "type": "string",
                "description": (
                    "Descrizione dettagliata del problema e del motivo per cui è "
                    "necessario l'intervento umano."
                ),
            },
        },
        "required": ["subject", "description"],
    },
}


def escalate(
    subject: str,
    description: str,
    company_id: UUID,
    conversation_id: UUID,
    supabase: Client,
) -> str:
    """Create an escalation ticket and mark the conversation as ESCALATED.

    Args:
        subject: Short title for the escalation.
        description: Detailed reason for escalation.
        company_id: Tenant identifier.
        conversation_id: Conversation this escalation is linked to.
        supabase: Supabase client instance.

    Returns:
        A confirmation string indicating the conversation has been escalated.
    """
    row = {
        "company_id": str(company_id),
        "conversation_id": str(conversation_id),
        "subject": subject,
        "description": description,
        "status": "open",
        "is_escalation": True,
    }
    try:
        result = supabase.table("tickets").insert(row).execute()
        if not result.data:
            logger.error(
                "escalate: ticket insert returned no data for conversation %s",
                conversation_id,
            )
            return "Errore interno durante l'escalation. Riprova o contatta il supporto."
        ticket_id = result.data[0]["id"]
    except Exception:
        logger.exception(
            "escalate: failed to insert ticket for conversation %s", conversation_id
        )
        return "Errore interno durante l'escalation. Riprova o contatta il supporto."

    try:
        supabase.table("conversations").update({"status": "escalated"}).eq(
            "id", str(conversation_id)
        ).execute()
    except Exception:
        logger.error(
            "escalate: ticket %s created but conversation %s status update failed",
            ticket_id,
            conversation_id,
        )
    return (
        f"Conversazione escalata a un operatore umano. "
        f"Motivo: {subject}. Il team ti contatterà al più presto."
    )
