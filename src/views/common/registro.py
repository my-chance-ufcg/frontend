import streamlit as st
import time

st.title("Criar Nova Conta")
st.markdown("Cadastre-se aqui para poder usar a plataforma.")

st.write("---")

# Tipo de Perfil
tipo_conta = st.radio(
    "Eu quero me cadastrar como:",
    ["Candidato", "Recrutador"],
    index=0
)

st.write("---")

# Formulário de Dados
nome = st.text_input("Nome Completo")
email = st.text_input("E-mail")

col1, col2 = st.columns(2)
with col1:
    senha = st.text_input("Senha", type="password")
with col2:
    confirmar_senha = st.text_input("Confirmar Senha", type="password")

st.write("")

# Cadastro
if st.button("Criar Conta", type="primary", use_container_width=True):
    if not nome or not email or not senha or not confirmar_senha:
        st.error("Por favor, preencha todos os campos para continuar.")
    elif senha != confirmar_senha:
        st.error("As senhas não coincidem. Tente novamente.")
    else:
        # POST (INSERT) no banco de dados
        st.success(f"Conta criada com sucesso, {nome.split()[0]}! Redirecionando para o login...")
        time.sleep(2)
        st.switch_page("src/views/common/login.py")

st.write("---")

# Atalho para quem já tem conta
st.markdown("<p style='text-align: center;'>Já possui uma conta?</p>", unsafe_allow_html=True)
if st.button("Voltar para o Login", use_container_width=True):
    st.switch_page("src/views/common/login.py")
                

