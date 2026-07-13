import streamlit as st

from src.domain.user_messages import friendly_error
from src.services.api_client import ApiError, register as api_register
from src.services.auth_session import apply_auth_session

ROLE_MAP = {
    "Candidato": "CANDIDATE",
    "Recrutador": "RECRUITER",
}

st.title("Criar Nova Conta")
st.markdown("Cadastre-se aqui para poder usar a plataforma.")

st.write("---")

tipo_conta = st.radio(
    "Eu quero me cadastrar como:",
    ["Candidato", "Recrutador"],
    index=0,
)

st.write("---")

nome = st.text_input("Nome Completo")
email = st.text_input("E-mail")

col1, col2 = st.columns(2)
with col1:
    senha = st.text_input("Senha", type="password")
with col2:
    confirmar_senha = st.text_input("Confirmar Senha", type="password")

st.write("")

if st.button("Criar Conta", type="primary", use_container_width=True):
    if not nome or not email or not senha or not confirmar_senha:
        st.error("Por favor, preencha todos os campos para continuar.")
    elif senha != confirmar_senha:
        st.error("As senhas não coincidem. Tente novamente.")
    elif len(senha) < 6:
        st.error("A senha deve ter pelo menos 6 caracteres.")
    else:
        try:
            auth_response = api_register(
                {
                    "nome": nome.strip(),
                    "email": email.strip(),
                    "senha": senha,
                    "role": ROLE_MAP[tipo_conta],
                }
            )
            apply_auth_session(auth_response)
            st.success(f"Conta criada com sucesso, {nome.split()[0]}!")
            st.rerun()
        except ApiError as error:
            st.error(friendly_error(error, "Não foi possível criar a conta. Verifique os dados informados."))

st.write("---")

st.markdown("<p style='text-align: center;'>Já possui uma conta?</p>", unsafe_allow_html=True)
if st.button("Voltar para o Login", use_container_width=True):
    st.switch_page("src/views/common/login.py")
