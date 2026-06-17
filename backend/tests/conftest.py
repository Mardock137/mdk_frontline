from uuid import uuid4

import pytest

import utils.rate_limit as rate_limit_module


@pytest.fixture
def company_id():
    return uuid4()


@pytest.fixture
def conversation_id():
    return uuid4()


@pytest.fixture(autouse=True)
def disable_rate_limiter():
    """Disabilita il rate limiter per tutti i test.

    Senza questa fixture, i test che colpiscono lo stesso endpoint più volte
    rischierebbero di scattare il limite e fallire in modo non deterministico.
    Il test dedicato al 429 sovrascrive questo comportamento localmente.
    """
    rate_limit_module.limiter.enabled = False
    yield
    rate_limit_module.limiter.enabled = True
