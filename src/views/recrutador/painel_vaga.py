from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

import streamlit as st

import plotly.graph_objects as go

from src.domain.catalog import SENIORITY_LEVELS, catalog_label
from src.domain.invite_status import format_datetime_human, render_job_description, schedule_status_badge
from src.domain.user_messages import friendly_error
from src.services.api_client import (
    ApiError,
    confirm_schedule,
    schedule_interview,
    send_invite,
)


def _format_experience_line(exp: dict[str, Any]) -> str:
    cargo = exp.get("cargo") or "Experiência"
    details: list[str] = []

    senioridade = exp.get("senioridade")
    if senioridade:
        details.append(catalog_label(SENIORITY_LEVELS, senioridade))

    if exp.get("tempo_meses") is not None:
        details.append(f"{exp['tempo_meses']} meses")
    elif exp.get("inicio_mes") and exp.get("inicio_ano"):
        start = f"{int(exp['inicio_mes']):02d}/{exp['inicio_ano']}"
        if exp.get("atual"):
            details.append(f"{start} — atual")
        elif exp.get("fim_mes") and exp.get("fim_ano"):
            details.append(f"{start} — {int(exp['fim_mes']):02d}/{exp['fim_ano']}")
        else:
            details.append(start)

    if details:
        return f"{cargo} ({', '.join(details)})"
    return cargo


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
    disponiveis = [item for item in recommendations if item.get("convite_status") != "RECUSADO"]
    recusados = [item for item in recommendations if item.get("convite_status") == "RECUSADO"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Candidatos disponíveis", len(disponiveis))
    with col2:
        st.metric("Recusaram convite", len(recusados))
    with col3:
        st.metric("Aguardando resposta", len(pending_invites))
    with col4:
        fully_confirmed = [
            item for item in confirmed_invites if item.get("schedule_status") == "CONFIRMED"
        ]
        st.metric("Entrevistas confirmadas", len(fully_confirmed))

    total_match = len(disponiveis) + len(recusados) + len(pending_invites) + len(confirmed_invites)
    total_convites = len(pending_invites) + len(confirmed_invites) + len(recusados)
    total_aceitos = len(confirmed_invites)
    total_agendados = len(fully_confirmed)

    if total_match > 0:
        st.write("---")
        
        fig = go.Figure(go.Funnel(
            y=["Sugeridos (Match)", "Convites Enviados", "Convites Aceitos", "Entrevistas Agendadas"],
            x=[total_match, total_convites, total_aceitos, total_agendados],
            textinfo="value+percent initial",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Candidatos: %{x}<br>"
                "%{percentInitial} do total inicial<br>"
                "%{percentPrevious} da etapa anterior"
                "<extra></extra>"
            ),
            marker={"color": ["#637085", "#225BFD", "#10B981", "#0f9f74"]} 
        ))

        fig.update_layout(
            margin={"t": 40, "b": 20, "l": 20, "r": 20},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=320,
            title={
                "text": "Pipeline de Conversão da Vaga", 
                "x": 0.5, 
                "font": {"color": "#202736", "size": 18, "family": "Plus Jakarta Sans"}
            }
        )

        st.plotly_chart(fig, use_container_width=True)


def _split_recommendations(
    recommendations: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    disponiveis = [item for item in recommendations if item.get("convite_status") != "RECUSADO"]
    recusados = [item for item in recommendations if item.get("convite_status") == "RECUSADO"]
    return disponiveis, recusados


def _render_recommendation_card(
    item: dict[str, Any],
    *,
    vaga_id: str | None = None,
    show_invite_button: bool = True,
    rejected: bool = False,
) -> None:
    score_pct = round(item["compatibilidade_score"] * 100, 1)
    posicao = item.get("posicao", "?")
    with st.container(border=True):
        st.markdown(f"#### #{posicao} — Perfil {item['candidato_id']}")
        if rejected:
            st.warning("Este candidato já recusou um convite para esta vaga.")
        st.markdown(f"**Compatibilidade:** {item['compatibilidade']} ({score_pct}%)")
        st.markdown(f"**Competências:** {', '.join(item['competencias_tecnicas'])}")

        if item.get("experiencias"):
            exp_lines = [_format_experience_line(exp) for exp in item["experiencias"]]
            st.markdown(f"**Experiências:** {', '.join(exp_lines)}")

        if show_invite_button and vaga_id:
            if st.button(
                "Enviar convite de entrevista",
                key=f"invite_{vaga_id}_{item['candidato_id']}",
            ):
                try:
                    send_invite(
                        vaga_id,
                        item["candidato_id"],
                        "Gostaríamos de agendar uma entrevista com você.",
                    )
                    st.toast("Convite enviado! Acompanhe em **Aguardando resposta**.")
                    st.rerun()
                except ApiError as error:
                    st.error(friendly_error(error, "Não foi possível enviar o convite."))


def render_suggestions_tab(vaga_id: str, recommendations: list[dict[str, Any]]) -> None:
    st.subheader("Candidatos compatíveis")
    st.caption(
        "Ordenados por aderência à vaga. Quem já tem convite pendente ou entrevista marcada "
        "não aparece aqui. Candidatos que recusaram permanecem listados apenas para referência."
    )

    if not recommendations:
        st.info(
            "Nenhum candidato disponível para convite nesta vaga no momento. "
            "Todos os perfis compatíveis já podem ter sido convidados, ou ainda não há candidatos adequados."
        )
        return

    disponiveis, recusados = _split_recommendations(recommendations)

    if disponiveis:
        with st.expander("Filtros Avançados"):
            col1, col2 = st.columns(2)
            
            with col1:
                min_score = st.slider(
                    "Compatibilidade mínima (%)", 
                    min_value=0, 
                    max_value=100, 
                    value=0, 
                    step=5,
                    help="Exibe apenas candidatos com score igual ou superior."
                )
                
                all_skills = sorted(list({
                    skill for c in disponiveis for skill in c.get("competencias_tecnicas", [])
                }))
                selected_skills = st.multiselect(
                    "Filtrar por competência específica", 
                    options=all_skills,
                    placeholder="Selecione uma ou mais..."
                )

            with col2:
                from src.domain.catalog import SENIORITY_LEVELS, catalog_label, catalog_keys
                
                seniority_keys = catalog_keys(SENIORITY_LEVELS)
                
                selected_seniority = st.multiselect(
                    "Filtrar por nível de senioridade",
                    options=seniority_keys,
                    format_func=lambda k: catalog_label(SENIORITY_LEVELS, k),
                    help="O candidato deve possuir ao menos uma experiência no nível selecionado.",
                    placeholder="Pleno, Sênior..."
                )
                
        filtered_disponiveis = []
        for item in disponiveis:
            score_pct = round(item["compatibilidade_score"] * 100, 1)
            
            if score_pct < min_score:
                continue
                
            if selected_skills:
                c_skills = item.get("competencias_tecnicas", [])
                if not all(s in c_skills for s in selected_skills):
                    continue
                    
            if selected_seniority:
                c_exps = item.get("experiencias", [])
                c_seniorities = [exp.get("senioridade") for exp in c_exps if exp.get("senioridade")]
                # O candidato precisa ter pelo menos uma experiência com a senioridade exigida no filtro
                if not any(s in c_seniorities for s in selected_seniority):
                    continue
                    
            filtered_disponiveis.append(item)
    else:
        filtered_disponiveis = []

    if filtered_disponiveis:
        st.markdown(f"#### Disponíveis para convite ({len(filtered_disponiveis)})")
        for item in filtered_disponiveis:
            _render_recommendation_card(item, vaga_id=vaga_id)
    elif disponiveis:
        st.warning("Nenhum candidato atende aos critérios dos filtros avançados. Tente ajustar a busca.")
    else:
        st.info("Nenhum candidato disponível para novo convite nesta vaga.")

    if recusados:
        st.markdown("#### Recusaram convite anteriormente")
        st.caption("Estes candidatos recusaram esta vaga e não podem receber novo convite.")
        for item in recusados:
            _render_recommendation_card(item, rejected=True, show_invite_button=False)


def render_pending_tab(pending_invites: list[dict[str, Any]]) -> None:
    if not pending_invites:
        st.info("Nenhum convite aguardando resposta.")
        return

    for invite in pending_invites:
        with st.container(border=True):
            st.markdown(f"**Perfil:** {invite['candidato_id']}")
            st.markdown(f"**Vaga:** {invite['titulo_vaga']}")
            render_job_description(invite)
            if invite.get("mensagem"):
                st.write(invite["mensagem"])
            st.caption("Os dados de contato ficam ocultos até o candidato aceitar o convite.")


def render_confirmed_tab(confirmed_invites: list[dict[str, Any]]) -> None:
    st.caption(
        "Depois que o candidato aceita, você vê nome, e-mail e telefone. "
        "Proponha data, horário e link da reunião — a entrevista só fica confirmada "
        "quando os dois concordarem."
    )

    if not confirmed_invites:
        st.info("Nenhuma entrevista confirmada ainda.")
        return

    for invite in confirmed_invites:
        with st.container(border=True):
            st.markdown(f"**Perfil:** {invite['candidato_id']}")
            st.markdown(f"**Vaga:** {invite['titulo_vaga']}")
            render_job_description(invite)

            badge = schedule_status_badge(invite, perspective="recruiter")
            if invite.get("schedule_status") == "CONFIRMED":
                st.success(badge)
            elif badge:
                st.info(badge)
            else:
                st.success("Candidato aceitou o convite.")

            if invite.get("candidato_nome"):
                st.markdown("#### Contato do candidato")
                st.markdown(f"**Nome:** {invite['candidato_nome']}")
                st.markdown(f"**E-mail:** [{invite['candidato_email']}](mailto:{invite['candidato_email']})")
                if invite.get("candidato_telefone"):
                    telefone = invite["candidato_telefone"]
                    digits = "".join(ch for ch in telefone if ch.isdigit())
                    tel_href = f"+55{digits}" if digits else telefone
                    st.markdown(f"**Telefone:** [{telefone}](tel:{tel_href})")

            _render_schedule_section(invite)


def _render_schedule_section(invite: dict[str, Any]) -> None:
    invite_id = invite["convite_id"]
    schedule_status = invite.get("schedule_status")
    existing_at = invite.get("proposed_interview_at")
    existing_link = invite.get("meeting_link") or ""

    if existing_at:
        st.markdown(f"**Horário proposto:** {format_datetime_human(existing_at)}")
    if existing_link:
        st.markdown(f"**Link da reunião:** [{existing_link}]({existing_link})")

    if schedule_status == "PROPOSED_BY_CANDIDATE":
        if st.button("Confirmar horário proposto pelo candidato", key=f"confirm_{invite_id}"):
            try:
                confirm_schedule(invite_id)
                st.toast("Entrevista confirmada!")
                st.rerun()
            except ApiError as error:
                st.error(friendly_error(error, "Não foi possível confirmar o horário."))

    can_propose = schedule_status in (
        "AWAITING_SCHEDULE",
        "PROPOSED_BY_CANDIDATE",
        "PROPOSED_BY_RECRUITER",
        None,
    )
    if schedule_status != "CONFIRMED" and can_propose:
        with st.expander(
            "Propor ou atualizar agendamento",
            expanded=schedule_status in ("AWAITING_SCHEDULE", "PROPOSED_BY_CANDIDATE", None),
        ):
            with st.form(key=f"schedule_{invite_id}"):
                interview_date = st.date_input("Data", value=date.today(), key=f"date_{invite_id}")
                interview_time = st.time_input(
                    "Horário", value=time(hour=10, minute=0), key=f"time_{invite_id}"
                )
                meet_link = st.text_input(
                    "Link Google Meet (opcional)",
                    value=existing_link,
                    placeholder="https://meet.google.com/...",
                    key=f"meet_{invite_id}",
                )

                if st.form_submit_button("Enviar proposta de horário"):
                    proposed = datetime.combine(interview_date, interview_time).isoformat() + "Z"
                    try:
                        schedule_interview(invite_id, proposed, meet_link or None)
                        st.toast("Proposta enviada ao candidato!")
                        st.rerun()
                    except ApiError as error:
                        st.error(friendly_error(error, "Não foi possível enviar a proposta de horário."))
