from uuid import uuid4

import pytest


@pytest.fixture
def company_id():
    return uuid4()


@pytest.fixture
def conversation_id():
    return uuid4()
