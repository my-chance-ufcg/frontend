import streamlit as st

from src.domain.user_messages import friendly_error
from src.services.api_client import ApiError, login as api_login
from src.services.auth_session import apply_auth_session
from src.ui.layout import render_auth_form_header, render_auth_shell_start

_, col_form = render_auth_shell_start()

with col_form:
    with st.container(border=True):
        render_auth_form_header(
            title="Bem-vindo de volta",
            subtitle="Entre com sua conta para acessar convites, currículo e oportunidades.",
        )

        tab_candidato, tab_recrutador = st.tabs(["Sou candidato", "Sou recrutador"])

        with tab_candidato:
            email_cand = st.text_input("E-mail", placeholder="seu-email@exemplo.com", key="cand_email")
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
                        st.error(friendly_error(error, "Não foi possível entrar. Verifique e-mail e senha."))
                else:
                    st.error("Preencha todos os campos.")

        with tab_recrutador:
            email_rec = st.text_input("E-mail corporativo", placeholder="seu-email@empresa.com.br", key="rec_email")
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
                        st.error(friendly_error(error, "Não foi possível entrar. Verifique e-mail e senha."))
                else:
                    st.error("Preencha todos os campos.")

        st.divider()
        st.caption("Ainda não tem conta?")
        st.page_link(
            "src/views/common/registro.py",
            label="Criar nova conta gratuitamente",
            icon=":material/person_add:",
            use_container_width=True,
        )
