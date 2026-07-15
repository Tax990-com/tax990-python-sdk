from __future__ import annotations

import re

# EIN pattern from ANALYSIS.md §Business Entity Fields
_EIN_RE = re.compile(r"^(\d{9}|\d{2}-\d{7})$")


def validate_ein(ein: str) -> bool:
    return bool(_EIN_RE.match(ein))


def format_ein(ein: str) -> str:
    """Formats a 9-digit EIN as XX-XXXXXXX."""
    digits = ein.replace("-", "")
    if len(digits) != 9 or not digits.isdigit():
        raise ValueError(f'Invalid EIN: "{ein}". Must be 9 digits.')
    return f"{digits[:2]}-{digits[2:]}"
