from __future__ import annotations

import streamlit as st

from src.domain.catalog import SKILL_OPTIONS


def render_skill_multiselect(
    label: str,
    *,
    key: str,
    default: list[str] | None = None,
    exclude_labels: list[str] | None = None,
) -> list[str]:
    default = default or []
    exclude = set(exclude_labels or [])
    options = [skill for skill in SKILL_OPTIONS if skill not in exclude]

    return st.multiselect(
        label,
        options=options,
        default=[item for item in default if item in options],
        key=key,
        placeholder="Digite para buscar...",
    )
