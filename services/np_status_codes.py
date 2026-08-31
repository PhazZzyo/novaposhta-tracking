# services/np_status_codes.py
"""
Business logic for Nova Poshta status codes.
Labels/translations live in translations/np_status.py - this module only
contains classification logic (which codes mean "delivered", "exception",
"at branch", etc).
"""

# Status codes that mean the package is considered delivered/finalized
# (matches is_delivered() logic in services/novaposhta.py)
DELIVERED_CODES = {'2', '9', '10', '11'}

# Status codes that represent an exception/problem requiring attention -
# not a normal in-transit state, and not a successful delivery either
EXCEPTION_CODES = {'102', '103', '104', '105', '111', '112'}

# Status codes meaning "arrived at branch, ready for pickup"
AT_BRANCH_CODES = {'7', '8'}


def is_exception_status(status_code):
	"""True if this status code represents a problem/exception, not normal transit."""
	return str(status_code) in EXCEPTION_CODES


def is_at_branch_status(status_code):
	"""True if this status code means arrived at branch, ready for pickup."""
	return str(status_code) in AT_BRANCH_CODES
