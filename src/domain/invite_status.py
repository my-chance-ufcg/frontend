from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from zoneinfo import ZoneInfo


def format_datetime_human(value: str | None, tz: str = "America/Sao_Paulo") -> str:
    if not value:
        return ""

    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return value

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=ZoneInfo("UTC"))

    local = parsed.astimezone(ZoneInfo(tz))
    return local.strftime("%d/%m/%Y às %H:%M")


def invite_history_label(
    convite: dict[str, Any],
    *,
    perspective: Literal["candidate", "recruiter"] = "recruiter",
) -> str:
    status = convite.get("status", "")
    schedule = convite.get("schedule_status")

    if status == "ENVIADO":
        if perspective == "candidate":
            return "Aguardando sua resposta"
        return "Aguardando resposta do candidato"
    if status == "RECUSADO":
        return "Proposta recusada"
    if status == "INVALIDADO":
        return "Convite encerrado"

    if status == "ACEITO":
        if schedule == "CONFIRMED":
            return "Entrevista confirmada"
        if schedule == "PROPOSED_BY_RECRUITER":
            if perspective == "candidate":
                return "Aceito — confirme o horário proposto"
            return "Aceito — aguardando confirmação do candidato"
        if schedule == "PROPOSED_BY_CANDIDATE":
            if perspective == "candidate":
                return "Aceito — aguardando resposta do recrutador"
            return "Aceito — aguardando sua confirmação do horário"
        return "Aceito — marcar entrevista"

    return status


def schedule_status_badge(
    convite: dict[str, Any],
    *,
    perspective: Literal["candidate", "recruiter"] = "candidate",
) -> str:
    schedule = convite.get("schedule_status")
    if schedule == "CONFIRMED":
        return "Entrevista confirmada por ambas as partes"
    if schedule == "PROPOSED_BY_RECRUITER":
        if perspective == "recruiter":
            return "Horário enviado — aguardando confirmação do candidato"
        return "Horário proposto pelo recrutador — aguardando sua confirmação"
    if schedule == "PROPOSED_BY_CANDIDATE":
        if perspective == "recruiter":
            return "Candidato propôs novo horário — aguardando sua confirmação"
        return "Novo horário proposto por você — aguardando confirmação do recrutador"
    if convite.get("status") == "ACEITO":
        if perspective == "recruiter":
            return "Aguardando agendamento pelo recrutador"
        return "Aguardando proposta de horário pelo recrutador"
    return ""


def render_job_description(convite: dict[str, Any]) -> None:
    import streamlit as st

    descricao = convite.get("descricao_vaga")
    if not descricao:
        return

    with st.expander("Descrição da vaga", expanded=convite.get("status") == "ENVIADO"):
        st.markdown(descricao)
