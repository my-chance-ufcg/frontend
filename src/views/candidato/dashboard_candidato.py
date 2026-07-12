import streamlit as st

from src.domain.catalog import INVITE_STATUS_LABELS
from src.services.api_client import ApiError, accept_invite, list_my_invites, reject_invite

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
    st.warning("Cadastre seu perfil anonimizado na página **Editar Meu Currículo** antes de gerenciar convites.")
    st.stop()

st.metric(label="Status do Perfil", value="Ativo / Anônimo")
st.caption(f"ID anônimo: `{candidato_id}`")
st.write("---")

try:
    convites = list_my_invites()
except ApiError as error:
    st.error(f"Não foi possível carregar convites: {error}")
    st.stop()

pendentes = [item for item in convites if item["status"] == "ENVIADO"]
confirmados = [item for item in convites if item["status"] == "ACEITO"]

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
                st.markdown(
                    f"**Status:** {INVITE_STATUS_LABELS.get(convite['status'], convite['status'])}"
                )
                if convite.get("mensagem"):
                    st.write(convite["mensagem"])
                st.info(
                    "Ao autorizar, seus dados pessoais (nome e e-mail) serão revelados ao recrutador. "
                    "A entrevista em si ocorrerá fora da plataforma."
                )

                col_aceitar, col_recusar = st.columns(2)
                with col_aceitar:
                    if st.button(
                        "Autorizar Revelação de Dados",
                        key=f"accept_{convite['convite_id']}",
                        use_container_width=True,
                    ):
                        try:
                            accept_invite(convite["convite_id"])
                            st.toast("Convite aceito! Seus dados foram autorizados para revelação.")
                            st.rerun()
                        except ApiError as error:
                            st.error(str(error))
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
                            st.error(str(error))

with aba_confirmadas:
    st.subheader("Entrevistas Confirmadas")
    st.caption(
        "Após autorizar a revelação, o recrutador poderá entrar em contato e "
        "registrar horário e link da entrevista."
    )

    if not confirmados:
        st.info("Nenhuma entrevista confirmada ainda.")
    else:
        for convite in confirmados:
            with st.container(border=True):
                st.markdown(f"### {convite['titulo_vaga']}")
                st.success("Você autorizou a revelação dos seus dados.")

                if convite.get("recruiter_nome"):
                    st.markdown("#### Contato do recrutador")
                    st.markdown(f"**Nome:** {convite['recruiter_nome']}")
                    st.markdown(
                        f"**E-mail:** [{convite['recruiter_email']}](mailto:{convite['recruiter_email']})"
                    )

                if convite.get("proposed_interview_at"):
                    st.markdown(f"**Horário proposto:** {convite['proposed_interview_at']}")
                else:
                    st.warning("Aguardando o recrutador definir data e horário.")

                if convite.get("meeting_link"):
                    st.markdown(f"**Link da reunião:** [{convite['meeting_link']}]({convite['meeting_link']})")

with aba_historico:
    st.subheader("Histórico de convites")
    if not convites:
        st.info("Nenhum convite registrado.")
    else:
        for convite in convites:
            st.markdown(
                f"- **{convite['titulo_vaga']}** — "
                f"{INVITE_STATUS_LABELS.get(convite['status'], convite['status'])}"
            )
