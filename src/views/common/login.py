import streamlit as st

# Estilo customizado
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("My Chance")
st.markdown("Onde seu perfil profissional é o mais importante") # Frase placholder, podemos pensar em outra depois
st.write("---")

tab_candidato, tab_recrutador = st.tabs(["Sou Candidato", "Sou Recrutador"])

# FLuxo candidato

with tab_candidato:
    st.subheader("Acesso do Candidato")
    email_cand = st.text_input("E-mail / Usuário", placeholder="seu-email@exemplo.com", key="cand_email")
    senha_cand = st.text_input("Senha", type="password", key="cand_pass")
    
    if st.button("Entrar", key="btn_cand", type="primary", use_container_width=True):
        if email_cand and senha_cand:
            st.session_state.user_role = "Candidato"
            st.rerun() 
        else:
            st.error("Preencha todos os campos.")

    st.markdown("""
        <div style='text-align: center; margin-top: 15px;'>
            <a href='#' style='text-decoration: none; color: #2E5BFF;'>Esqueci minha senha</a><br>
            <a href='#' style='text-decoration: none; color: #2E5BFF;'>Não tem cadastro? Crie seu perfil</a>
        </div>
    """, unsafe_allow_html=True)

# Fluxo recrutador

with tab_recrutador:
    st.subheader("Acesso do Recrutador")
    email_rec = st.text_input("E-mail corporativo / Usuário", placeholder="seu-email@empresa.com.br", key="rec_email")
    senha_rec = st.text_input("Senha", type="password", key="rec_pass")
    
    if st.button("Entrar", key="btn_rec", type="primary", use_container_width=True):
        if email_rec and senha_rec:
            st.session_state.user_role = "Recrutador"
            st.rerun()
        else:
            st.error("Preencha todos os campos.")
            
    st.markdown("""
        <div style='text-align: center; margin-top: 15px;'>
            <a href='#' style='text-decoration: none; color: #2E5BFF;'>Esqueci minha senha</a><br>
            <a href='#' style='text-decoration: none; color: #2E5BFF;'>Não tem cadastro? Crie sua conta corporativa</a>
        </div>
    """, unsafe_allow_html=True)
