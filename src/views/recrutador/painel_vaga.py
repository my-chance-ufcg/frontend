from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

import streamlit as st

from src.domain.catalog import (
    SENIORITY_LEVELS, 
    SALARY_RANGES,
    SOFT_SKILL_LABELS,
    BENEFIT_LABELS,
    catalog_label,
    catalog_keys
)
from src.domain.skill_picker import render_soft_skill_multiselect, render_benefit_multiselect
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


def _label_to_key(labels_dict: dict, label: str) -> str:
    for k, v in labels_dict.items():
        if v == label:
            return k
    return label


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
        with st.expander("Filtros Avançados", expanded=False):
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                filtro_soft = render_soft_skill_multiselect("Soft Skills", key=f"f_soft_{vaga_id}")
            with col_f2:
                filtro_ben = render_benefit_multiselect("Benefícios Desejados", key=f"f_ben_{vaga_id}")
            with col_f3:
                salary_keys = catalog_keys(SALARY_RANGES)
                filtro_salario = st.selectbox(
                    "Faixa Salarial do Candidato",
                    options=[None, *salary_keys],
                    format_func=lambda key: "Qualquer" if key is None else catalog_label(SALARY_RANGES, key),
                    key=f"f_sal_{vaga_id}"
                )

        if filtro_soft or filtro_ben or filtro_salario:
            soft_keys_set = {_label_to_key(SOFT_SKILL_LABELS, s) for s in filtro_soft}
            ben_keys_set = {_label_to_key(BENEFIT_LABELS, b) for b in filtro_ben}
            
            filtrados = []
            for item in disponiveis:
                cand_soft = set(item.get("soft_skills") or [])
                cand_ben = set(item.get("beneficios") or [])
                cand_salario = item.get("faixa_salarial")
                
                match_soft = soft_keys_set.issubset(cand_soft) if soft_keys_set else True
                match_ben = ben_keys_set.issubset(cand_ben) if ben_keys_set else True
                match_sal = (cand_salario == filtro_salario) if filtro_salario else True
                
                if match_soft and match_ben and match_sal:
                    filtrados.append(item)
            disponiveis = filtrados

        st.markdown(f"#### Disponíveis para convite ({len(disponiveis)})")
        if disponiveis:
            for item in disponiveis:
                _render_recommendation_card(item, vaga_id=vaga_id)
        else:
            st.warning("Nenhum candidato corresponde aos filtros avançados aplicados.")
    else:
        st.info("Nenhum candidato disponível para novo convite nesta vaga.")

    if recusados:
        st.markdown("#### Recusaram convite anteriormente")
        st.caption("Estes candidatos recusaram esta vaga e não podem receber novo convite.")
        for item in recusados:
            _render_recommendation_card(item, rejected=True, show_invite_button=False)


def render_pending_tab(pending_invites: list[dict[str, Any]]) -> None:
    st.info("**Proteção de Dados:** Os dados sensíveis (Nome, E-mail, Telefone e Foto) dos candidatos estão ocultos por padrão. Eles serão revelados de forma transparente assim que o candidato aceitar o convite.")
    
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


def render_confirmed_tab(confirmed_invites: list[dict[str, Any]]) -> None:
    st.success("**Perfil Revelado:** O candidato aceitou o convite. Você já pode visualizar os dados de contato e propor um horário para entrevista.")
    st.caption(
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