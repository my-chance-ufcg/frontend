from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

import streamlit as st

from src.services.api_client import ApiError, schedule_interview, send_invite


def render_job_selector(jobs: list[dict[str, Any]]) -> str | None:
    if not jobs:
        return None

    options = {job["vaga_id"]: job["titulo"] for job in jobs}
    default_id = st.session_state.get("vaga_id")
    if default_id not in options:
        default_id = jobs[0]["vaga_id"]

    selected_id = st.selectbox(
        "Selecione a vaga",
        options=list(options.keys()),
        index=list(options.keys()).index(default_id),
        format_func=lambda job_id: options[job_id],
        key="recruiter_job_selector",
    )
    st.session_state.vaga_id = selected_id
    return selected_id


def render_job_metrics(
    recommendations: list[dict[str, Any]],
    pending_invites: list[dict[str, Any]],
    confirmed_invites: list[dict[str, Any]],
) -> None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sugestões disponíveis", len(recommendations))
    with col2:
        st.metric("Aguardando resposta", len(pending_invites))
    with col3:
        st.metric("Entrevistas confirmadas", len(confirmed_invites))


def render_suggestions_tab(vaga_id: str, recommendations: list[dict[str, Any]]) -> None:
    st.subheader("Perfis anonimizados ranqueados pelo NLP")
    st.caption(
        "Candidatos já convidados ou com entrevista confirmada não aparecem aqui — "
        "consulte as outras abas."
    )

    if not recommendations:
        st.info(
            "Nenhum candidato disponível para convite nesta vaga. "
            "Isso pode ocorrer quando todos os compatíveis já foram convidados "
            "ou quando nenhum perfil passa nos filtros de compatibilidade."
        )
        return

    for item in recommendations:
        score_pct = round(item["compatibilidade_score"] * 100, 1)
        posicao = item.get("posicao", "?")
        with st.container(border=True):
            st.markdown(f"#### #{posicao} — {item['candidato_id']}")
            st.markdown(f"**Compatibilidade:** {item['compatibilidade']} ({score_pct}%)")
            st.markdown(f"**Skills:** {', '.join(item['competencias_tecnicas'])}")

            if item.get("experiencias"):
                exp_lines = [
                    f"{exp['cargo']} ({exp['tempo_meses']} meses)"
                    for exp in item["experiencias"]
                ]
                st.markdown(f"**Experiências:** {', '.join(exp_lines)}")

            if st.button(
                "Enviar convite de entrevista",
                key=f"invite_{vaga_id}_{item['candidato_id']}",
            ):
                try:
                    send_invite(
                        vaga_id,
                        item["candidato_id"],
                        "Gostaríamos de agendar uma entrevista com base no seu perfil técnico.",
                    )
                    st.toast("Convite enviado! O candidato foi movido para Aguardando Resposta.")
                    st.rerun()
                except ApiError as error:
                    st.error(str(error))


def render_pending_tab(pending_invites: list[dict[str, Any]]) -> None:
    if not pending_invites:
        st.info("Nenhum convite aguardando resposta.")
        return

    for invite in pending_invites:
        with st.container(border=True):
            st.markdown(f"**Candidato:** `{invite['candidato_id']}`")
            st.markdown(f"**Vaga:** {invite['titulo_vaga']}")
            if invite.get("mensagem"):
                st.write(invite["mensagem"])
            st.caption("Dados pessoais ocultos até o candidato autorizar a revelação.")


def render_confirmed_tab(confirmed_invites: list[dict[str, Any]]) -> None:
    st.caption(
        "Após o aceite mútuo, os dados pessoais são revelados. "
        "A entrevista ocorre fora da plataforma — use o agendamento abaixo "
        "para registrar horário e link (ex.: Google Meet)."
    )

    if not confirmed_invites:
        st.info("Nenhuma entrevista confirmada ainda.")
        return

    for invite in confirmed_invites:
        with st.container(border=True):
            st.markdown(f"**ID anônimo:** `{invite['candidato_id']}`")
            st.markdown(f"**Vaga:** {invite['titulo_vaga']}")
            st.success("Candidato autorizou revelação de dados.")

            if invite.get("candidato_nome"):
                st.markdown("#### Dados revelados")
                st.markdown(f"**Nome:** {invite['candidato_nome']}")
                st.markdown(f"**E-mail:** [{invite['candidato_email']}](mailto:{invite['candidato_email']})")

            _render_schedule_form(invite)


def _render_schedule_form(invite: dict[str, Any]) -> None:
    invite_id = invite["convite_id"]
    existing_at = invite.get("proposed_interview_at")
    existing_link = invite.get("meeting_link") or ""

    if existing_at:
        st.info(f"Horário proposto: **{existing_at}**")
    if existing_link:
        st.markdown(f"**Link da reunião:** [{existing_link}]({existing_link})")

    with st.expander("Agendar entrevista", expanded=not existing_at):
        with st.form(key=f"schedule_{invite_id}"):
            interview_date = st.date_input("Data", value=date.today(), key=f"date_{invite_id}")
            interview_time = st.time_input("Horário", value=time(hour=10, minute=0), key=f"time_{invite_id}")
            meet_link = st.text_input(
                "Link Google Meet (opcional)",
                value=existing_link,
                placeholder="https://meet.google.com/...",
                key=f"meet_{invite_id}",
            )

            if st.form_submit_button("Salvar agendamento"):
                proposed = datetime.combine(interview_date, interview_time).isoformat() + "Z"
                try:
                    schedule_interview(invite_id, proposed, meet_link or None)
                    st.toast("Agendamento salvo!")
                    st.rerun()
                except ApiError as error:
                    st.error(str(error))
