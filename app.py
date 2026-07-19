import streamlit as st

from src.ui.paths import LOGO_FAVICON, LOGO_SYMBOL_COLOR
from src.ui.theme import inject_theme

st.set_page_config(
    page_title="MyChance",
    page_icon=str(LOGO_FAVICON),
    layout="wide",
    initial_sidebar_state="expanded",
)

if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "candidato_id" not in st.session_state:
    st.session_state.candidato_id = None
if "vaga_id" not in st.session_state:
    st.session_state.vaga_id = None

is_authenticated = st.session_state.user_role is not None
inject_theme(auth_page=not is_authenticated)

page_login = st.Page(
    "src/views/common/login.py",
    title="Entrar",
    icon=":material/login:",
    default=not is_authenticated,
)
page_registro = st.Page(
    "src/views/common/registro.py",
    title="Criar conta",
    icon=":material/person_add:",
)

page_dashboard_cand = st.Page(
    "src/views/candidato/dashboard_candidato.py",
    title="Início",
    icon=":material/inbox:",
    default=True,
)
page_cv = st.Page(
    "src/views/candidato/cadastro_cv.py",
    title="Meu currículo",
    icon=":material/description:",
)

page_dashboard_rec = st.Page(
    "src/views/recrutador/dashboard_recrutador.py",
    title="Vagas ativas",
    icon=":material/work:",
    default=True,
)
page_vagas = st.Page(
    "src/views/recrutador/criar_vaga.py",
    title="Publicar vaga",
    icon=":material/add_business:",
)

if st.session_state.user_role == "Candidato":
    if LOGO_SYMBOL_COLOR.exists():
        st.logo(str(LOGO_SYMBOL_COLOR), size="small")
    pg = st.navigation([page_dashboard_cand, page_cv], position="sidebar")
elif st.session_state.user_role == "Recrutador":
    if LOGO_SYMBOL_COLOR.exists():
        st.logo(str(LOGO_SYMBOL_COLOR), size="small")
    pg = st.navigation([page_dashboard_rec, page_vagas], position="sidebar")
else:
    pg = st.navigation([page_login, page_registro], position="top")

pg.run()

if is_authenticated:
    with st.sidebar:
        st.markdown('<div class="mc-sidebar-footer-marker"></div>', unsafe_allow_html=True)
        st.markdown(f"**{st.session_state.user_role}**")
        st.caption("Sessão ativa")
        if st.button("Sair da conta", use_container_width=True):
            from src.services.auth_session import clear_auth_session

            clear_auth_session()
            st.rerun()
