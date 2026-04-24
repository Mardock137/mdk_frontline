"""Tests for api/agent.py endpoint (all external calls mocked)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

import api.agent as agent_module
from main import app
from utils.config import Settings


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def company_id():
    return uuid4()


@pytest.fixture
def conversation_id():
    return uuid4()


@pytest.fixture
def agent_config_row(company_id):
    return {
        "id": str(uuid4()),
        "company_id": str(company_id),
        "agent_name": "Frontline",
        "company_display_name": "Acme Corp",
        "logo_url": None,
        "primary_color": "#000000",
        "tone": "formal",
        "default_language": "it",
        "welcome_message": "Hello!",
        "updated_at": "2026-01-01T00:00:00Z",
    }


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        agent_module,
        "get_settings",
        lambda: Settings(ANTHROPIC_API_KEY="test-key"),
    )
    return TestClient(app)


def _make_supabase(company_id, conversation_id, agent_config_row):
    """Build a minimal Supabase mock covering all queries the endpoint makes."""
    supabase = MagicMock()

    def table_side_effect(name):
        tbl = MagicMock()
        if name == "companies":
            tbl.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
                data=[{"id": str(company_id)}]
            )
        elif name == "agent_configs":
            tbl.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
                data=[agent_config_row]
            )
        elif name == "conversations":
            tbl.insert.return_value.execute.return_value = MagicMock(
                data=[{"id": str(conversation_id)}]
            )
        elif name == "messages":
            tbl.select.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
                data=[]
            )
            tbl.insert.return_value.execute.return_value = MagicMock(data=[])
        return tbl

    supabase.table.side_effect = table_side_effect
    return supabase


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_send_message_creates_new_conversation(
    client, monkeypatch, company_id, conversation_id, agent_config_row
):
    supabase = _make_supabase(company_id, conversation_id, agent_config_row)
    monkeypatch.setattr(agent_module, "get_supabase_client", lambda: supabase)
    monkeypatch.setattr(
        agent_module, "get_llm_client", lambda **kw: MagicMock()
    )

    async def fake_run(self, input_data):
        return {"reply": "Risposta agente."}

    monkeypatch.setattr(agent_module.SupportAgent, "run", fake_run)

    response = client.post(
        "/chat/acme/message",
        json={"content": "Ciao"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["conversation_id"] == str(conversation_id)
    assert body["reply"] == "Risposta agente."


def test_send_message_reuses_existing_conversation(
    client, monkeypatch, company_id, conversation_id, agent_config_row
):
    supabase = _make_supabase(company_id, conversation_id, agent_config_row)
    monkeypatch.setattr(agent_module, "get_supabase_client", lambda: supabase)
    monkeypatch.setattr(
        agent_module, "get_llm_client", lambda **kw: MagicMock()
    )

    async def fake_run(self, input_data):
        return {"reply": "Ok."}

    monkeypatch.setattr(agent_module.SupportAgent, "run", fake_run)

    response = client.post(
        "/chat/acme/message",
        json={"conversation_id": str(conversation_id), "content": "Altra domanda"},
    )

    assert response.status_code == 200
    assert response.json()["conversation_id"] == str(conversation_id)


def test_send_message_404_when_company_not_found(
    client, monkeypatch, company_id, conversation_id, agent_config_row
):
    supabase = MagicMock()
    supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
        data=[]
    )
    monkeypatch.setattr(agent_module, "get_supabase_client", lambda: supabase)

    response = client.post("/chat/nonexistent/message", json={"content": "Ciao"})

    assert response.status_code == 404


def test_send_message_404_when_agent_config_missing(
    client, monkeypatch, company_id, conversation_id, agent_config_row
):
    supabase = MagicMock()

    def table_side_effect(name):
        tbl = MagicMock()
        if name == "companies":
            tbl.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
                data=[{"id": str(company_id)}]
            )
        elif name == "agent_configs":
            tbl.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
                data=[]
            )
        return tbl

    supabase.table.side_effect = table_side_effect
    monkeypatch.setattr(agent_module, "get_supabase_client", lambda: supabase)

    response = client.post("/chat/acme/message", json={"content": "Ciao"})

    assert response.status_code == 404


def test_send_message_rejects_empty_content(
    client, monkeypatch, company_id, conversation_id, agent_config_row
):
    monkeypatch.setattr(
        agent_module, "get_supabase_client", lambda: MagicMock()
    )

    response = client.post("/chat/acme/message", json={"content": ""})

    assert response.status_code == 422


def test_send_message_500_when_api_key_missing(
    monkeypatch, company_id, conversation_id, agent_config_row
):
    monkeypatch.setattr(
        agent_module,
        "get_settings",
        lambda: Settings(ANTHROPIC_API_KEY=""),
    )
    supabase = _make_supabase(company_id, conversation_id, agent_config_row)
    monkeypatch.setattr(agent_module, "get_supabase_client", lambda: supabase)

    test_client = TestClient(app)
    response = test_client.post("/chat/acme/message", json={"content": "Ciao"})

    assert response.status_code == 500
