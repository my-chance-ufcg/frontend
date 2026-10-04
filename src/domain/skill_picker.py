from __future__ import annotations

import streamlit as st

from src.domain.catalog import (
    SKILL_OPTIONS,
    SOFT_SKILL_OPTIONS,
    BENEFIT_OPTIONS,
)


def _render_generic_multiselect(
    label: str,
    *,
    key: str,
    catalog_options: list[str],
    default: list[str] | None = None,
    exclude_labels: list[str] | None = None,
) -> list[str]:
    """Função base para renderizar os multiselects evitando duplicação de código."""
    default = default or []
    exclude = set(exclude_labels or [])
    options = [item for item in catalog_options if item not in exclude]

    # Evita conflito Streamlit de default + key: só inicializa o estado se ainda não existir.
    if key not in st.session_state:
        st.session_state[key] = [item for item in default if item in options]

    return st.multiselect(
        label,
        options=options,
        key=key,
        placeholder="Digite para buscar...",
    )


def render_skill_multiselect(
    label: str,
    *,
    key: str,
    default: list[str] | None = None,
    exclude_labels: list[str] | None = None,
) -> list[str]:
    return _render_generic_multiselect(
        label=label,
        key=key,
        catalog_options=SKILL_OPTIONS,
        default=default,
        exclude_labels=exclude_labels,
    )


def render_soft_skill_multiselect(
    label: str,
    *,
    key: str,
    default: list[str] | None = None,
    exclude_labels: list[str] | None = None,
) -> list[str]:
    return _render_generic_multiselect(
        label=label,
        key=key,
        catalog_options=SOFT_SKILL_OPTIONS,
        default=default,
        exclude_labels=exclude_labels,
    )


def render_benefit_multiselect(
    label: str,
    *,
    key: str,
    default: list[str] | None = None,
    exclude_labels: list[str] | None = None,
) -> list[str]:
    return _render_generic_multiselect(
        label=label,
        key=key,
        catalog_options=BENEFIT_OPTIONS,
        default=default,
        exclude_labels=exclude_labels,
    )