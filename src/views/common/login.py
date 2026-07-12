import streamlit as st

from src.services.api_client import ApiError, login as api_login
from src.services.auth_session import apply_auth_session

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("My Chance")
st.markdown("Onde seu perfil profissional é o mais importante")
st.write("---")

tab_candidato, tab_recrutador = st.tabs(["Sou Candidato", "Sou Recrutador"])

with tab_candidato:
    st.subheader("Acesso do Candidato")
    email_cand = st.text_input("E-mail / Usuário", placeholder="seu-email@exemplo.com", key="cand_email")
    senha_cand = st.text_input("Senha", type="password", key="cand_pass")

    if st.button("Entrar", key="btn_cand", type="primary", use_container_width=True):
        if email_cand and senha_cand:
            try:
                apply_auth_session(api_login({"email": email_cand.strip(), "senha": senha_cand}))
                if st.session_state.user_role != "Candidato":
                    from src.services.auth_session import clear_auth_session

                    clear_auth_session()
                    st.error("Esta conta não é de candidato.")
                else:
                    st.rerun()
            except ApiError as error:
                st.error(f"Não foi possível entrar: {error}")
        else:
            st.error("Preencha todos os campos.")

with tab_recrutador:
    st.subheader("Acesso do Recrutador")
    email_rec = st.text_input("E-mail corporativo / Usuário", placeholder="seu-email@empresa.com.br", key="rec_email")
    senha_rec = st.text_input("Senha", type="password", key="rec_pass")

    if st.button("Entrar", key="btn_rec", type="primary", use_container_width=True):
        if email_rec and senha_rec:
            try:
                apply_auth_session(api_login({"email": email_rec.strip(), "senha": senha_rec}))
                if st.session_state.user_role != "Recrutador":
                    from src.services.auth_session import clear_auth_session

                    clear_auth_session()
                    st.error("Esta conta não é de recrutador.")
                else:
                    st.rerun()
            except ApiError as error:
                st.error(f"Não foi possível entrar: {error}")
        else:
            st.error("Preencha todos os campos.")

st.info("Conta demo de recrutador (Docker/dev): `recruiter@mychance.local` / `recruiter123`")
