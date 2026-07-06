import streamlit as st

from src.domain.catalog import INVITE_STATUS_LABELS
from src.services.api_client import ApiError, accept_invite, list_candidate_invites, reject_invite

st.title("Painel do Candidato")

candidato_id = st.session_state.get("candidato_id")
if not candidato_id:
    st.warning("Cadastre seu perfil anonimizado na página **Editar Meu Currículo** antes de gerenciar convites.")
    st.stop()

st.metric(label="Status do Perfil", value="Ativo / Anônimo")
st.caption(f"ID anônimo: `{candidato_id}`")
st.write("---")

st.subheader("Convites para Entrevista")

try:
    convites = list_candidate_invites(candidato_id)
except ApiError as error:
    st.error(f"Não foi possível carregar convites: {error}")
    st.stop()

pendentes = [item for item in convites if item["status"] == "ENVIADO"]

if not pendentes:
    st.info("Nenhum convite pendente no momento.")
else:
    for convite in pendentes:
        with st.container(border=True):
            st.markdown(f"### {convite['titulo_vaga']}")
            st.markdown(f"**Status:** {INVITE_STATUS_LABELS.get(convite['status'], convite['status'])}")
            if convite.get("mensagem"):
                st.write(convite["mensagem"])
            st.info("Ao autorizar, seus dados pessoais poderão ser revelados ao recrutador.")

            col_aceitar, col_recusar = st.columns(2)
            with col_aceitar:
                if st.button("Autorizar Revelação de Dados", key=f"accept_{convite['convite_id']}", use_container_width=True):
                    try:
                        accept_invite(convite["convite_id"])
                        st.toast("Convite aceito!")
                        st.rerun()
                    except ApiError as error:
                        st.error(str(error))
            with col_recusar:
                if st.button("Recusar Proposta", key=f"reject_{convite['convite_id']}", use_container_width=True):
                    try:
                        reject_invite(convite["convite_id"])
                        st.toast("Convite recusado.")
                        st.rerun()
                    except ApiError as error:
                        st.error(str(error))

if convites:
    with st.expander("Histórico de convites"):
        for convite in convites:
            st.markdown(
                f"- **{convite['titulo_vaga']}** — "
                f"{INVITE_STATUS_LABELS.get(convite['status'], convite['status'])}"
            )
