"""Login errors must retain the server's explanation."""

import asyncio
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def api_module(monkeypatch):
    root = Path(__file__).parents[1] / "custom_components" / "mazda_6e"
    package = ModuleType("login_api_test")
    package.__path__ = [str(root)]
    exceptions = ModuleType("homeassistant.exceptions")
    exceptions.ConfigEntryAuthFailed = type("ConfigEntryAuthFailed", (Exception,), {})
    monkeypatch.setitem(sys.modules, "homeassistant", ModuleType("homeassistant"))
    monkeypatch.setitem(sys.modules, "homeassistant.exceptions", exceptions)
    monkeypatch.setitem(sys.modules, package.__name__, package)
    for name in ("const", "credential_crypto", "models", "mqtt", "api"):
        spec = importlib.util.spec_from_file_location(
            f"{package.__name__}.{name}", root / f"{name}.py",
        )
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, spec.name, module)
        spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("code", ["CAC_1_1_01_020", "CAC_1_1_01_040"])
@pytest.mark.parametrize("message", ["Synthetic login rejection", None, "", "  ", {"unexpected": "value"}])
def test_login_rejection_keeps_code_and_message(api_module, code, message):
    response = {
        "success": False, "code": code,
        "data": {"token": "private-token", "refreshToken": "private-refresh"},
    }
    if message is not None:
        response["msg"] = message
    session = MagicMock()
    session.post.return_value.__aenter__ = AsyncMock(
        return_value=MagicMock(json=AsyncMock(return_value=response)),
    )
    api = api_module.Mazda6EApi(
        session, control_public_key="public-key", region="europe",
    )

    with pytest.raises(api_module.MazdaLoginError) as caught:
        asyncio.run(api.login_email_password("encrypted-email", "encrypted-password"))

    error = caught.value
    assert error.code == code
    expected = message if isinstance(message, str) and message.strip() else "No error message returned by Mazda"
    assert error.message == expected
    assert expected in str(error)
    assert "private-token" not in str(error)
    assert "private-refresh" not in str(error)
    assert api.token is None
    assert api.refresh is None


def test_login_message_stays_on_one_log_line(api_module):
    error = api_module.MazdaLoginError("test-code", "  First line\r\nsecond line\t ")
    assert error.message == "First line second line"
