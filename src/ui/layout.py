from __future__ import annotations

import streamlit as st

from src.ui.paths import LOGO_HORIZONTAL


def render_page_header(
    *,
    title: str,
    subtitle: str | None = None,
    eyebrow: str | None = None,
    badge: str | None = None,
) -> None:
    if eyebrow:
        st.caption(eyebrow.upper())
    st.title(title)
    if subtitle:
        st.markdown(subtitle)
    if badge:
        st.success(badge)


def render_section(title: str, caption: str | None = None) -> None:
    st.subheader(title)
    if caption:
        st.caption(caption)


def _render_brand_panel() -> None:
    st.markdown('<div class="mc-auth-brand-marker"></div>', unsafe_allow_html=True)
    if LOGO_HORIZONTAL.exists():
        st.image(str(LOGO_HORIZONTAL), use_container_width=True)
    st.markdown("#### Conexões anônimas, **matches reais.**")
    st.markdown(
        "A plataforma que protege seus dados até o momento certo e prioriza "
        "compatibilidade técnica entre candidatos e oportunidades."
    )
    st.markdown(
        """
        - Perfil anonimizado até aceitar convite
        - Matching por competências, idiomas e fit de vaga
        - Fluxo profissional para candidatos e recrutadores
        """
    )


def render_auth_shell_start() -> tuple:
    col_brand, col_form = st.columns([1, 1], gap="large", vertical_alignment="center")
    with col_brand:
        _render_brand_panel()
    return col_brand, col_form


def render_auth_form_header(*, title: str, subtitle: str) -> None:
    st.markdown('<div class="mc-auth-form-marker"></div>', unsafe_allow_html=True)
    st.markdown(f"### {title}")
    st.caption(subtitle)
