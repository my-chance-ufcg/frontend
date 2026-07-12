import streamlit as st

from src.services.api_client import ApiError, get_recommendations, get_sample_job_id, list_job_invites, send_invite

st.title("Painel do Recrutador")

vaga_id = st.session_state.get("vaga_id")
if not vaga_id:
    try:
        vaga_id = get_sample_job_id()
    except ApiError:
        vaga_id = None
    if vaga_id:
        st.session_state.vaga_id = vaga_id

if not vaga_id:
    st.warning("Nenhuma vaga ativa. Crie uma em **Criar Nova Vaga**.")
    st.stop()

try:
    recommendations = get_recommendations(vaga_id)
    invites = list_job_invites(vaga_id)
except ApiError as error:
    st.error(f"Erro ao consultar o backend: {error}")
    st.stop()

aceitos = [item for item in invites if item["status"] == "ACEITO"]
pendentes = [item for item in invites if item["status"] == "ENVIADO"]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Candidatos compatíveis", len(recommendations))
with col2:
    st.metric("Convites pendentes", len(pendentes))
with col3:
    st.metric("Entrevistas confirmadas", len(aceitos))

st.caption(f"Vaga ativa: `{vaga_id}`")
st.write("---")

aba_sugestoes, aba_pendentes, aba_confirmadas = st.tabs(
    ["Sugestões de Matching", "Aguardando Resposta", "Entrevistas Confirmadas"]
)

with aba_sugestoes:
    st.subheader("Perfis anonimizados ranqueados pelo NLP")
    if not recommendations:
        st.info("Nenhum candidato compatível encontrado.")
    for item in recommendations:
        score_pct = round(item["compatibilidade_score"] * 100, 1)
        with st.container(border=True):
            st.markdown(f"#### {item['candidato_id']}")
            st.markdown(f"**Compatibilidade:** {item['compatibilidade']} ({score_pct}%)")
            st.markdown(f"**Skills:** {', '.join(item['competencias_tecnicas'])}")
            if st.button("Enviar convite de entrevista", key=f"invite_{item['candidato_id']}"):
                try:
                    send_invite(
                        vaga_id,
                        item["candidato_id"],
                        "Gostaríamos de agendar uma entrevista com base no seu perfil técnico.",
                    )
                    st.toast("Convite enviado!")
                    st.rerun()
                except ApiError as error:
                    st.error(str(error))

with aba_pendentes:
    if not pendentes:
        st.info("Nenhum convite aguardando resposta.")
    for invite in pendentes:
        with st.container(border=True):
            st.markdown(f"**Candidato:** {invite['candidato_id']}")
            st.markdown(f"**Vaga:** {invite['titulo_vaga']}")
            st.caption("Dados pessoais ainda ocultos.")

with aba_confirmadas:
    if not aceitos:
        st.info("Nenhuma entrevista confirmada ainda.")
    for invite in aceitos:
        with st.container(border=True):
            st.markdown(f"**Candidato:** {invite['candidato_id']}")
            st.markdown(f"**Vaga:** {invite['titulo_vaga']}")
            st.success("Candidato autorizou revelação de dados.")
