import streamlit as st

from src.services.api_client import ApiError, login as api_login

ROLE_LABELS = {
    "CANDIDATE": "Candidato",
    "RECRUITER": "Recrutador",
}


def apply_auth_session(auth_response: dict) -> None:
    st.session_state.auth_token = auth_response["token"]
    st.session_state.user_id = auth_response["user_id"]
    st.session_state.user_role = ROLE_LABELS.get(auth_response["role"], auth_response["role"])
    st.session_state.candidato_id = auth_response.get("candidato_id")


def clear_auth_session() -> None:
    st.session_state.auth_token = None
    st.session_state.user_id = None
    st.session_state.user_role = None
    st.session_state.candidato_id = None
    st.session_state.vaga_id = None
