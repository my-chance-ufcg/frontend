from __future__ import annotations

import re


_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")


def normalize_email(value: str | None) -> str | None:
    if value is None:
        return None
    email = value.strip().lower()
    return email or None


def is_valid_email(value: str | None) -> bool:
    email = normalize_email(value)
    return bool(email and _EMAIL_RE.fullmatch(email))


def normalize_phone(value: str | None) -> str | None:
    """Keep digits only for validation, then format as Brazilian (XX) XXXXX-XXXX or (XX) XXXX-XXXX."""
    if value is None:
        return None

    digits = re.sub(r"\D", "", value.strip())
    if digits.startswith("55") and len(digits) >= 12:
        digits = digits[2:]

    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return None


def is_valid_phone(value: str | None) -> bool:
    return normalize_phone(value) is not None
