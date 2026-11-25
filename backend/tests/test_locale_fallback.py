"""Smoke tests for the Spanish default locale and Accept-Language prefix matching."""
import os

import pytest
from flask import Flask

from app.utils import locale as locale_mod
from app.utils.locale import get_language_instruction, get_locale, match_locale, set_locale, t


def _clear_thread_locale():
    if hasattr(locale_mod._thread_local, "locale"):
        delattr(locale_mod._thread_local, "locale")


@pytest.fixture(autouse=True)
def _reset_locale(monkeypatch):
    monkeypatch.delenv("DEFAULT_LOCALE", raising=False)
    _clear_thread_locale()
    yield
    _clear_thread_locale()


def test_default_locale_is_spanish():
    assert get_locale() == "es"
    assert "México" in get_language_instruction()
    assert "Predice todo" in t("meta.title")
    assert "预测" not in t("meta.title")


def test_browser_spanish_prefixes_map_to_es():
    app = Flask(__name__)
    for header in ("es-MX", "es-ES", "es_MX", "es-MX,es;q=0.9,en;q=0.8"):
        with app.test_request_context(headers={"Accept-Language": header}):
            assert get_locale() == "es", header


def test_other_language_prefixes_still_match():
    app = Flask(__name__)
    with app.test_request_context(headers={"Accept-Language": "en-US,en;q=0.9"}):
        assert get_locale() == "en"
    with app.test_request_context(headers={"Accept-Language": "zh-CN"}):
        assert get_locale() == "zh"
        assert "中文" in get_language_instruction() or "请使用中文" in get_language_instruction()


def test_unknown_language_falls_back_to_spanish():
    app = Flask(__name__)
    with app.test_request_context(headers={"Accept-Language": "fr-FR,fr;q=0.8"}):
        assert get_locale() == "es"
        assert t("common.confirm") != "Confirm"


def test_default_locale_env_overrides_fallback(monkeypatch):
    monkeypatch.setenv("DEFAULT_LOCALE", "en")
    app = Flask(__name__)
    with app.test_request_context(headers={"Accept-Language": "fr"}):
        assert get_locale() == "en"
    set_locale(None)
    assert get_locale() == "en"
    monkeypatch.setenv("DEFAULT_LOCALE", "es-MX")
    _clear_thread_locale()
    assert match_locale(os.environ["DEFAULT_LOCALE"]) == "es"
    assert get_locale() == "es"
