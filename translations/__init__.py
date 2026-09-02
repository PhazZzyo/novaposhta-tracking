# translations/__init__.py
"""
Translations package.

Split by domain to keep files small and reviewable:
- common.py         nav, generic actions (save, cancel, close, edit...)
- auth.py           login, users, admin
- packages.py       package list, dashboard, sync, invoice
- package_form.py   create/edit package modal, seats, validation
- settings.py       settings page + telegram settings
- bot.py            Telegram bot messages (separate, unrelated message set)
- np_status.py      official Nova Poshta status code labels

"""
from .common import COMMON_TRANSLATIONS
from .auth import AUTH_TRANSLATIONS
from .packages import PACKAGES_TRANSLATIONS
from .package_form import PACKAGE_FORM_TRANSLATIONS
from .settings import SETTINGS_TRANSLATIONS
from .bot import BOT_TRANSLATIONS, t_bot
from .np_status import NP_STATUS_LABELS, get_status_label


def _merge(*dicts):
	"""Merge multiple {'en': {...}, 'uk': {...}} translation dicts into one."""
	merged = {'en': {}, 'uk': {}}
	for d in dicts:
		for lang in ('en', 'uk'):
			merged[lang].update(d.get(lang, {}))
	return merged


TRANSLATIONS = _merge(
	COMMON_TRANSLATIONS,
	AUTH_TRANSLATIONS,
	PACKAGES_TRANSLATIONS,
	PACKAGE_FORM_TRANSLATIONS,
	SETTINGS_TRANSLATIONS,
)

__all__ = ['TRANSLATIONS', 'BOT_TRANSLATIONS', 't_bot', 'NP_STATUS_LABELS', 'get_status_label']