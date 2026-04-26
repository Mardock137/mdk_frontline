"""Tests for agents/support_agent.py (all external calls mocked)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

import agents.support_agent as agent_module
from agents.support_agent import SupportAgent, _FALLBACK_REPLY
from database.models import AgentConfig, AgentTone, ConversationStatus
from integrations.llm_interfaces.base_llm_interface import ChatResponse, ToolUse


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def company_id():
    return uuid4()


@pytest.fixture
def conversation_id():
    return uuid4()


@pytest.fixture
def agent_config(company_id):
    return AgentConfig(
        id=uuid4(),
        company_id=company_id,
        agent_name="Frontline",
        company_display_name="Acme Corp",
        tone=AgentTone.FORMAL,
        default_language="it",
        updated_at="2026-01-01T00:00:00Z",
    )


@pytest.fixture
def supabase():
    sb = MagicMock()
    sb.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
        data=[]
    )
    sb.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
    return sb


@pytest.fixture
def llm():
    return MagicMock()


@pytest.fixture
def support_agent(company_id, agent_config, llm, supabase):
    return SupportAgent(
        company_id=company_id,
        agent_config=agent_config,
        llm=llm,
        supabase=supabase,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _text_response(text: str) -> ChatResponse:
    return ChatResponse(stop_reason="end_turn", text=text, tool_uses=[], raw_content=[])


def _tool_response(tool_name: str, tool_input: dict) -> ChatResponse:
    tool_id = "tool_abc123"
    raw = [{"type": "tool_use", "id": tool_id, "name": tool_name, "input": tool_input}]
    return ChatResponse(
        stop_reason="tool_use",
        text=None,
        tool_uses=[ToolUse(id=tool_id, name=tool_name, input=tool_input)],
        raw_content=raw,
    )


# ---------------------------------------------------------------------------
# Tests: run()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_returns_direct_reply(support_agent, llm, conversation_id):
    llm.chat = AsyncMock(return_value=_text_response("Ciao! Come posso aiutarti?"))

    result = await support_agent.run(
        {"conversation_id": conversation_id, "content": "Ciao"}
    )

    assert result["reply"] == "Ciao! Come posso aiutarti?"


@pytest.mark.asyncio
async def test_run_saves_messages_to_db(support_agent, llm, supabase, conversation_id):
    llm.chat = AsyncMock(return_value=_text_response("Risposta agente."))

    await support_agent.run(
        {"conversation_id": conversation_id, "content": "Domanda cliente."}
    )

    supabase.table.return_value.insert.assert_called()
    inserted = supabase.table.return_value.insert.call_args[0][0]
    roles = [r["role"] for r in inserted]
    assert "customer" in roles
    assert "agent" in roles


@pytest.mark.asyncio
async def test_run_with_knowledge_tool(
    support_agent, llm, supabase, monkeypatch, company_id, conversation_id
):
    async def fake_search_knowledge(query, *, company_id, **kwargs):
        return "[1] Risposta dalla KB."

    monkeypatch.setattr(agent_module.knowledge, "search_knowledge", fake_search_knowledge)

    llm.chat = AsyncMock(
        side_effect=[
            _tool_response("search_knowledge", {"query": "Come si resetta?"}),
            _text_response("Ecco la risposta: [1] Risposta dalla KB."),
        ]
    )

    result = await support_agent.run(
        {"conversation_id": conversation_id, "content": "Come si resetta?"}
    )

    assert result["reply"] == "Ecco la risposta: [1] Risposta dalla KB."
    assert llm.chat.call_count == 2


@pytest.mark.asyncio
async def test_run_with_ticket_tool(
    support_agent, llm, supabase, monkeypatch, conversation_id
):
    def fake_create_ticket(subject, description, company_id, conversation_id, supabase):
        return "Ticket creato con ID: abc-123"

    monkeypatch.setattr(agent_module.ticket, "create_ticket", fake_create_ticket)

    llm.chat = AsyncMock(
        side_effect=[
            _tool_response("create_ticket", {"subject": "Bug", "description": "Dettaglio"}),
            _text_response("Ho aperto un ticket per te."),
        ]
    )

    result = await support_agent.run(
        {"conversation_id": conversation_id, "content": "C'è un bug"}
    )

    assert result["reply"] == "Ho aperto un ticket per te."


@pytest.mark.asyncio
async def test_run_with_escalation_tool(
    support_agent, llm, supabase, monkeypatch, conversation_id
):
    def fake_escalate(subject, description, company_id, conversation_id, supabase):
        return "Conversazione escalata."

    monkeypatch.setattr(agent_module.escalation, "escalate", fake_escalate)

    llm.chat = AsyncMock(
        side_effect=[
            _tool_response("escalate", {"subject": "Urgente", "description": "Sistema giù"}),
            _text_response("Ho escalato la tua richiesta."),
        ]
    )

    result = await support_agent.run(
        {"conversation_id": conversation_id, "content": "Emergenza!"}
    )

    assert result["reply"] == "Ho escalato la tua richiesta."


@pytest.mark.asyncio
async def test_run_returns_fallback_on_max_iterations(support_agent, llm, monkeypatch, conversation_id):
    monkeypatch.setattr(agent_module, "_MAX_ITERATIONS", 2)

    async def fake_search_knowledge(query, *, company_id, **kwargs):
        return "result"

    monkeypatch.setattr(agent_module.knowledge, "search_knowledge", fake_search_knowledge)

    llm.chat = AsyncMock(
        return_value=_tool_response("search_knowledge", {"query": "loop"})
    )

    result = await support_agent.run(
        {"conversation_id": conversation_id, "content": "Loop"}
    )

    assert result["reply"] == _FALLBACK_REPLY


@pytest.mark.asyncio
async def test_run_unknown_tool_returns_error_string(
    support_agent, llm, conversation_id
):
    llm.chat = AsyncMock(
        side_effect=[
            _tool_response("nonexistent_tool", {}),
            _text_response("Risposta finale."),
        ]
    )

    result = await support_agent.run(
        {"conversation_id": conversation_id, "content": "test"}
    )

    second_call_messages = llm.chat.call_args_list[1][0][0]
    tool_result_block = second_call_messages[-1]["content"][0]
    assert "non riconosciuto" in tool_result_block["content"]


@pytest.mark.asyncio
async def test_execute_tool_returns_error_when_search_knowledge_query_missing(
    support_agent, conversation_id
):
    result = await support_agent._execute_tool(
        "search_knowledge", {}, conversation_id
    )

    assert "mancante" in result


@pytest.mark.asyncio
async def test_execute_tool_returns_error_when_create_ticket_params_missing(
    support_agent, conversation_id
):
    result = await support_agent._execute_tool(
        "create_ticket", {}, conversation_id
    )

    assert "mancanti" in result


@pytest.mark.asyncio
async def test_execute_tool_returns_error_when_escalate_params_missing(
    support_agent, conversation_id
):
    result = await support_agent._execute_tool("escalate", {}, conversation_id)

    assert "mancanti" in result


@pytest.mark.asyncio
async def test_load_history_converts_roles(support_agent, supabase, conversation_id):
    supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
        data=[
            {"role": "customer", "content": "Ciao"},
            {"role": "agent", "content": "Ciao, come posso aiutarti?"},
            {"role": "system", "content": "system note"},
        ]
    )

    history = support_agent._load_history(conversation_id)

    assert len(history) == 2
    assert history[0] == {"role": "user", "content": "Ciao"}
    assert history[1] == {"role": "assistant", "content": "Ciao, come posso aiutarti?"}
