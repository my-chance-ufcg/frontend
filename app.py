import streamlit as st

# Configuração inicial da página
st.set_page_config(page_title="My Chance | Bem-vindo", page_icon="🎯", layout="centered")

# Estilo para tirar o menu padrão do Streamlit
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Título e Subtítulo
st.title("My Chance")
st.markdown("Onde seu perfil profissional é o mais importante")
st.write("---")

# Criação das abas de navegação
tab_candidato, tab_recrutador = st.tabs(["Sou Candidato", "Sou Recrutador"])

# Fluxo do candidato
with tab_candidato:
    st.subheader("Acesso do Candidato")
    
    # Campos de input
    email_cand = st.text_input("E-mail / Usuário", placeholder="seu-email@exemplo.com", key="cand_email")
    senha_cand = st.text_input("Senha", type="password", key="cand_pass")
    
    # Botão de Login
    if st.button("Entrar", key="btn_cand", type="primary", use_container_width=True):
        if email_cand and senha_cand:
            st.success("Autenticação bem-sucedida! Redirecionando para o seu currículo anônimo...")
            # Aqui entrará a lógica de redirecionamento no futuro
        else:
            st.error("Preencha todos os campos.")

    # Links de rodapé
    st.markdown("""
        <div style='text-align: center; margin-top: 15px;'>
            <a href='#' style='text-decoration: none; color: #2E5BFF;'>Esqueci minha senha</a><br>
            <a href='#' style='text-decoration: none; color: #2E5BFF;'>Não tem cadastro? Crie seu perfil</a>
        </div>
    """, unsafe_allow_html=True)

# Fluxo do recrutador
with tab_recrutador:
    st.subheader("Acesso do Recrutador")
    
    # Campos de input
    email_rec = st.text_input("E-mail corporativo / Usuário", placeholder="seu-email@empresa.com.br", key="rec_email")
    senha_rec = st.text_input("Senha", type="password", key="rec_pass")
    
    # Botão de Login
    if st.button("Entrar", key="btn_rec", type="primary", use_container_width=True):
        if email_rec and senha_rec:
            st.success("Autenticação bem-sucedida! Carregando talentos recomendados...")
            # Colocar lógica de redirecionamento!
        else:
            st.error("Preencha todos os campos corretamente.")
            
    # Links de rodapé
    st.markdown("""
        <div style='text-align: center; margin-top: 15px;'>
            <a href='#' style='text-decoration: none; color: #2E5BFF;'>Esqueci minha senha</a><br>
            <a href='#' style='text-decoration: none; color: #2E5BFF;'>Não tem cadastro? Crie sua conta corporativa</a>
        </div>
    """, unsafe_allow_html=True)
