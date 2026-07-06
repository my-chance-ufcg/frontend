import streamlit as st

st.set_page_config(page_title="My Chance", layout="centered")

if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "candidato_id" not in st.session_state:
    st.session_state.candidato_id = None
if "vaga_id" not in st.session_state:
    st.session_state.vaga_id = None

# Mapeamento

# Antes de fazer login
page_login = st.Page("src/views/common/login.py", title="Fazer Login")
page_registro = st.Page("src/views/common/registro.py", title="Criar Conta")

# Candidato
page_dashboard_cand = st.Page("src/views/candidato/dashboard_candidato.py", title="Painel do Candidato")
page_cv = st.Page("src/views/candidato/cadastro_cv.py", title="Editar Meu Currículo")

# Recrutador
page_dashboard_rec = st.Page("src/views/recrutador/dashboard_recrutador.py", title="Painel do Recrutador")
page_vagas = st.Page("src/views/recrutador/criar_vaga.py", title="Criar Nova Vaga")


# Lógica de Roteamento
if st.session_state.user_role == "Candidato":
    pg = st.navigation([page_dashboard_cand, page_cv]) 
elif st.session_state.user_role == "Recrutador":
    pg = st.navigation([page_dashboard_rec, page_vagas])
else:
    pg = st.navigation([page_login, page_registro])

pg.run()

# Botão para sair
if st.session_state.user_role is not None:
    with st.sidebar:
        st.markdown("<div style='height: 50vh;'></div>", unsafe_allow_html=True)
        st.write("---") 
        if st.button("Sair", use_container_width=True):
            st.session_state.user_role = None
            st.rerun()
