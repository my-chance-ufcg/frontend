from datetime import date, datetime, time

import streamlit as st

from src.domain.invite_status import format_datetime_human, invite_history_label, render_job_description, schedule_status_badge
from src.domain.user_messages import friendly_error
from src.services.api_client import (
    ApiError,
    accept_invite,
    confirm_schedule,
    counter_propose_schedule,
    list_my_invites,
    reject_invite,
)

st.session_state.pop("cv_save_feedback", None)
st.session_state._active_page = "dashboard_candidato"

st.title("Painel do Candidato")

candidato_id = st.session_state.get("candidato_id")
if not candidato_id and st.session_state.get("auth_token"):
    try:
        from src.services.api_client import get_my_profile

        profile = get_my_profile()
        candidato_id = profile["candidato_id"]
        st.session_state.candidato_id = candidato_id
    except ApiError:
        candidato_id = None

if not candidato_id:
    st.warning("Complete seu currículo em **Editar Meu Currículo** para receber convites de entrevista.")
    st.stop()

st.metric(label="Seu perfil", value="Ativo")
st.caption("Recrutadores enxergam suas competências; seus dados pessoais só são compartilhados se você aceitar um convite.")
st.write("---")

try:
    convites = list_my_invites()
except ApiError as error:
    st.error(friendly_error(error, "Não foi possível carregar seus convites. Tente novamente."))
    st.stop()

pendentes = [item for item in convites if item["status"] == "ENVIADO"]
confirmados = [item for item in convites if item["status"] == "ACEITO"]


def _render_candidate_schedule_actions(convite: dict) -> None:
    invite_id = convite["convite_id"]
    schedule_status = convite.get("schedule_status")

    if schedule_status == "PROPOSED_BY_RECRUITER":
        col_confirm, col_counter = st.columns(2)
        with col_confirm:
            if st.button("Confirmar presença", key=f"cand_confirm_{invite_id}", use_container_width=True):
                try:
                    confirm_schedule(invite_id)
                    st.toast("Presença confirmada! Entrevista agendada.")
                    st.rerun()
                except ApiError as error:
                    st.error(friendly_error(error, "Não foi possível confirmar o horário."))

        with col_counter:
            with st.expander("Propor outro horário"):
                with st.form(key=f"cand_counter_{invite_id}"):
                    new_date = st.date_input("Nova data", value=date.today())
                    new_time = st.time_input("Novo horário", value=time(hour=14, minute=0))
                    if st.form_submit_button("Enviar contraproposta"):
                        proposed = datetime.combine(new_date, new_time).isoformat() + "Z"
                        try:
                            counter_propose_schedule(invite_id, proposed, convite.get("meeting_link"))
                            st.toast("Contraproposta enviada ao recrutador!")
                            st.rerun()
                        except ApiError as error:
                            st.error(friendly_error(error, "Não foi possível enviar a contraproposta."))

    elif schedule_status == "PROPOSED_BY_CANDIDATE":
        st.warning("Aguardando o recrutador confirmar o novo horário que você propôs.")


aba_pendentes, aba_confirmadas, aba_historico = st.tabs(
    ["Convites Pendentes", "Entrevistas Confirmadas", "Histórico"]
)

with aba_pendentes:
    st.subheader("Convites para Entrevista")

    if not pendentes:
        st.info("Nenhum convite pendente no momento.")
    else:
        for convite in pendentes:
            with st.container(border=True):
                st.markdown(f"### {convite['titulo_vaga']}")
                st.markdown(f"**Situação:** {invite_history_label(convite, perspective='candidate')}")
                render_job_description(convite)
                if convite.get("mensagem"):
                    st.write(convite["mensagem"])
                st.info(
                    "Se aceitar, seu nome e e-mail serão compartilhados com o recrutador para agendar a entrevista."
                )

                col_aceitar, col_recusar = st.columns(2)
                with col_aceitar:
                    if st.button(
                        "Aceitar convite",
                        key=f"accept_{convite['convite_id']}",
                        use_container_width=True,
                    ):
                        try:
                            accept_invite(convite["convite_id"])
                            st.toast("Convite aceito! Seus dados de contato foram compartilhados.")
                            st.rerun()
                        except ApiError as error:
                            st.error(friendly_error(error, "Não foi possível aceitar o convite."))
                with col_recusar:
                    if st.button(
                        "Recusar Proposta",
                        key=f"reject_{convite['convite_id']}",
                        use_container_width=True,
                    ):
                        try:
                            reject_invite(convite["convite_id"])
                            st.toast("Convite recusado.")
                            st.rerun()
                        except ApiError as error:
                            st.error(friendly_error(error, "Não foi possível recusar o convite."))

with aba_confirmadas:
    st.subheader("Entrevistas Confirmadas")
    st.caption(
        "Quando o recrutador propor um horário, você pode confirmar presença "
        "ou sugerir outro horário. A entrevista fica 100% confirmada quando ambos concordarem."
    )

    if not confirmados:
        st.info("Nenhuma entrevista confirmada ainda.")
    else:
        for convite in confirmados:
            with st.container(border=True):
                st.markdown(f"### {convite['titulo_vaga']}")

                badge = schedule_status_badge(convite, perspective="candidate")
                if convite.get("schedule_status") == "CONFIRMED":
                    st.success(badge)
                elif badge:
                    st.info(badge)

                render_job_description(convite)

                if convite.get("recruiter_nome"):
                    st.markdown("#### Contato do recrutador")
                    st.markdown(f"**Nome:** {convite['recruiter_nome']}")
                    st.markdown(
                        f"**E-mail:** [{convite['recruiter_email']}](mailto:{convite['recruiter_email']})"
                    )

                if convite.get("proposed_interview_at"):
                    st.markdown(
                        f"**Horário proposto:** {format_datetime_human(convite['proposed_interview_at'])}"
                    )
                elif convite.get("schedule_status") == "AWAITING_SCHEDULE":
                    st.warning("Aguardando o recrutador definir data e horário.")

                if convite.get("meeting_link"):
                    st.markdown(
                        f"**Link da reunião:** [{convite['meeting_link']}]({convite['meeting_link']})"
                    )

                _render_candidate_schedule_actions(convite)

with aba_historico:
    st.subheader("Histórico de convites")
    if not convites:
        st.info("Nenhum convite registrado.")
    else:
        for convite in convites:
            label = invite_history_label(convite, perspective="candidate")
            st.markdown(f"- **{convite['titulo_vaga']}** — {label}")
