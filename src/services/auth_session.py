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
    st.session_state.pop("cv_save_feedback", None)
    st.session_state.pop("_cv_initialized", None)
    st.session_state.pop("_cv_data", None)
    st.session_state.pop("_active_page", None)
    for key in list(st.session_state.keys()):
        if str(key).startswith("cv_") or str(key).startswith("cargo_") or str(key).startswith("skill_"):
            st.session_state.pop(key, None)
