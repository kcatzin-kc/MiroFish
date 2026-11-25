import json
import os
import threading
from flask import request, has_request_context

_thread_local = threading.local()

_locales_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'locales')

# Load language registry
with open(os.path.join(_locales_dir, 'languages.json'), 'r', encoding='utf-8') as f:
    _languages = json.load(f)

# Load translation files
_translations = {}
for filename in os.listdir(_locales_dir):
    if filename.endswith('.json') and filename != 'languages.json':
        locale_name = filename[:-5]
        with open(os.path.join(_locales_dir, filename), 'r', encoding='utf-8') as f:
            _translations[locale_name] = json.load(f)


def _lookup_exact(token: str):
    if not token:
        return None
    if token in _translations:
        return token
    lower = token.lower()
    for name in _translations:
        if name.lower() == lower:
            return name
    return None


def match_locale(raw: str):
    """Map a locale tag or Accept-Language list onto a loaded catalog.

    `es-MX`, `es-ES` and `es_*` resolve to `es`. The first supported tag wins.
    """
    if raw is None:
        return None
    text = str(raw).strip()
    if not text:
        return None

    tokens = []
    for part in text.split(','):
        token = part.split(';', 1)[0].strip().replace('_', '-')
        if token and token != '*':
            tokens.append(token)
    if not tokens:
        tokens = [text.replace('_', '-')]

    for token in tokens:
        exact = _lookup_exact(token)
        if exact:
            return exact
        prefix = token.split('-', 1)[0]
        exact = _lookup_exact(prefix)
        if exact:
            return exact
    return None


def _default_locale() -> str:
    """Configured fallback. Unset or unknown values resolve to Spanish."""
    configured = os.environ.get('DEFAULT_LOCALE', 'es')
    return match_locale(configured) or 'es'


def set_locale(locale: str = None):
    """Set locale for the current thread. Call at the start of background threads."""
    _thread_local.locale = match_locale(locale) or _default_locale()


def get_locale() -> str:
    if has_request_context():
        matched = match_locale(request.headers.get('Accept-Language', ''))
        if matched:
            return matched
        return _default_locale()
    thread_locale = getattr(_thread_local, 'locale', None)
    if thread_locale:
        return match_locale(thread_locale) or _default_locale()
    return _default_locale()


def _lookup(locale: str, key: str):
    messages = _translations.get(locale, {})
    value = messages
    for part in key.split('.'):
        if isinstance(value, dict):
            value = value.get(part)
        else:
            return None
    if isinstance(value, str):
        return value
    return None


def t(key: str, **kwargs) -> str:
    locale = get_locale()
    value = _lookup(locale, key)
    if value is None:
        fallback = _default_locale()
        if fallback != locale:
            value = _lookup(fallback, key)
    if value is None and locale != 'zh' and _default_locale() != 'zh':
        value = _lookup('zh', key)

    if value is None:
        return key

    if kwargs:
        for k, v in kwargs.items():
            value = value.replace(f'{{{k}}}', str(v))

    return value


def get_language_instruction() -> str:
    locale = get_locale()
    lang_config = _languages.get(locale) or _languages.get(_default_locale()) or {}
    return lang_config.get('llmInstruction', 'Responde en español de México, con trato de tú.')
