"""Tests for tools/escalation.py (Supabase client mocked)."""

from unittest.mock import MagicMock, call
from uuid import uuid4

from tools.escalation import TOOL_DEFINITION, escalate


def _make_supabase() -> MagicMock:
    supabase = MagicMock()
    supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
        data=[{"id": str(uuid4())}]
    )
    supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[]
    )
    return supabase


def test_escalate_inserts_ticket_with_is_escalation_true():
    company_id = uuid4()
    conversation_id = uuid4()
    supabase = _make_supabase()

    escalate(
        subject="Critical issue",
        description="The system is down.",
        company_id=company_id,
        conversation_id=conversation_id,
        supabase=supabase,
    )

    insert_call_args = supabase.table.return_value.insert.call_args[0][0]
    assert insert_call_args["is_escalation"] is True
    assert insert_call_args["company_id"] == str(company_id)
    assert insert_call_args["conversation_id"] == str(conversation_id)


def test_escalate_updates_conversation_status():
    conversation_id = uuid4()
    supabase = _make_supabase()

    escalate(
        subject="Urgent",
        description="Details.",
        company_id=uuid4(),
        conversation_id=conversation_id,
        supabase=supabase,
    )

    supabase.table.return_value.update.assert_called_with({"status": "escalated"})
    supabase.table.return_value.update.return_value.eq.assert_called_with(
        "id", str(conversation_id)
    )


def test_escalate_returns_confirmation_message():
    supabase = _make_supabase()

    result = escalate(
        subject="Broken feature",
        description="Details.",
        company_id=uuid4(),
        conversation_id=uuid4(),
        supabase=supabase,
    )

    assert "escalata" in result.lower() or "operatore" in result.lower()


def test_tool_definition_schema():
    assert TOOL_DEFINITION["name"] == "escalate"
    props = TOOL_DEFINITION["input_schema"]["properties"]
    assert "subject" in props
    assert "description" in props
    assert set(TOOL_DEFINITION["input_schema"]["required"]) == {"subject", "description"}
