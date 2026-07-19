import streamlit as st

from src.domain.contact_validation import is_valid_email, is_valid_phone, normalize_email, normalize_phone
from src.domain.user_messages import friendly_error
from src.services.api_client import ApiError, register as api_register
from src.services.auth_session import apply_auth_session
from src.ui.layout import render_auth_form_header, render_auth_shell_start

ROLE_MAP = {
    "Candidato": "CANDIDATE",
    "Recrutador": "RECRUITER",
}

_, col_form = render_auth_shell_start()

with col_form:
    with st.container(border=True):
        render_auth_form_header(
            title="Criar nova conta",
            subtitle="Cadastre-se para publicar seu perfil ou gerenciar vagas na plataforma.",
        )

        tipo_conta = st.radio(
            "Eu quero me cadastrar como:",
            ["Candidato", "Recrutador"],
            index=0,
            horizontal=True,
        )

        nome = st.text_input("Nome completo")
        email = st.text_input("E-mail", placeholder="seu-email@exemplo.com")
        telefone = st.text_input(
            "Telefone",
            placeholder="(83) 99999-9999",
        )

        col1, col2 = st.columns(2)
        with col1:
            senha = st.text_input("Senha", type="password")
        with col2:
            confirmar_senha = st.text_input("Confirmar senha", type="password")

        if st.button("Criar conta", type="primary", use_container_width=True):
            email_normalizado = normalize_email(email)
            telefone_normalizado = normalize_phone(telefone)

            if not nome or not email or not senha or not confirmar_senha:
                st.error("Por favor, preencha todos os campos para continuar.")
            elif not is_valid_email(email):
                st.error("Informe um e-mail válido.")
            elif tipo_conta == "Candidato" and not is_valid_phone(telefone):
                st.error("Informe um telefone válido com DDD (10 ou 11 dígitos).")
            elif tipo_conta == "Recrutador" and telefone.strip() and not is_valid_phone(telefone):
                st.error("Informe um telefone válido com DDD (10 ou 11 dígitos), ou deixe em branco.")
            elif senha != confirmar_senha:
                st.error("As senhas não coincidem. Tente novamente.")
            elif len(senha) < 6:
                st.error("A senha deve ter pelo menos 6 caracteres.")
            else:
                try:
                    payload = {
                        "nome": nome.strip(),
                        "email": email_normalizado,
                        "senha": senha,
                        "role": ROLE_MAP[tipo_conta],
                    }
                    if telefone_normalizado:
                        payload["telefone"] = telefone_normalizado

                    auth_response = api_register(payload)
                    apply_auth_session(auth_response)
                    st.success(f"Conta criada com sucesso, {nome.split()[0]}!")
                    st.rerun()
                except ApiError as error:
                    st.error(friendly_error(error, "Não foi possível criar a conta. Verifique os dados informados."))

        st.divider()
        st.caption("Já possui uma conta?")
        st.page_link(
            "src/views/common/login.py",
            label="Entrar na plataforma",
            icon=":material/login:",
            use_container_width=True,
        )
