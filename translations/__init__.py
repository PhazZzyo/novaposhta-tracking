# translations/__init__.py
"""
Translations package.

For now this just re-exports the existing flat TRANSLATIONS dict from
_legacy.py so all existing `from translations import TRANSLATIONS` imports
across app.py/routes/templates keep working unchanged.

The bot has its own separate, smaller translation set in bot.py since its
message set is unrelated to the web app's UI strings.

TODO (next session): split _legacy.py into common.py, auth.py, packages.py,
package_form.py, settings.py - merge them all into TRANSLATIONS here, and
dedupe the handful of keys that currently exist more than once in
_legacy.py (e.g. 'sender', 'recipient', 'package_created', 'save_as_draft').
"""
from ._legacy import TRANSLATIONS
from .bot import BOT_TRANSLATIONS, t_bot

__all__ = ['TRANSLATIONS', 'BOT_TRANSLATIONS', 't_bot']