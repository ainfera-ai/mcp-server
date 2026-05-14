import os

import pytest


@pytest.fixture(autouse=True)
def _ainfera_env(monkeypatch):
    monkeypatch.setenv("AINFERA_API_KEY", "test-key")
    monkeypatch.setenv("AINFERA_API_BASE", "https://api.test.ainfera.ai")
    yield
