from __future__ import annotations

import requests

from src.config import FIREBASE_API_KEY, FIREBASE_PROJECT_ID
from src.services.api_client import ApiError, idp_login, login as api_login, register as api_register

_FIREBASE_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts:{action}?key={api_key}"

_ERROR_MESSAGES = {
    "EMAIL_EXISTS": "Já existe uma conta com este e-mail no provedor de identidade.",
    "EMAIL_NOT_FOUND": "E-mail ou senha incorretos. Tente novamente.",
    "INVALID_PASSWORD": "E-mail ou senha incorretos. Tente novamente.",
    "INVALID_LOGIN_CREDENTIALS": "E-mail ou senha incorretos. Tente novamente.",
    "WEAK_PASSWORD : Password should be at least 6 characters": "A senha deve ter pelo menos 6 caracteres.",
}


def firebase_configured() -> bool:
    return bool(FIREBASE_API_KEY and FIREBASE_PROJECT_ID)


def login_account(email: str, password: str) -> dict:
    if not firebase_configured():
        return api_login({"email": email, "senha": password})
    return idp_login(_firebase_password_grant("signInWithPassword", email, password))


def register_account(payload: dict) -> dict:
    if not firebase_configured():
        return api_register(payload)
    id_token = _firebase_password_grant("signUp", payload["email"], payload["senha"])
    profile = {
        "nome": payload["nome"],
        "role": payload["role"],
    }
    if payload.get("telefone"):
        profile["telefone"] = payload["telefone"]
    return idp_login(id_token, profile)


def _firebase_password_grant(action: str, email: str, password: str) -> str:
    response = requests.post(
        _FIREBASE_AUTH_URL.format(action=action, api_key=FIREBASE_API_KEY),
        json={"email": email, "password": password, "returnSecureToken": True},
        timeout=20,
    )
    if response.ok:
        token = response.json().get("idToken")
        if not token:
            raise ApiError("O provedor de identidade não devolveu um token.", response.status_code)
        return token

    message = _firebase_error_message(response)
    status = 401 if "senha" in message.lower() or "incorret" in message.lower() else response.status_code
    raise ApiError(message, status)


def _firebase_error_message(response: requests.Response) -> str:
    try:
        raw = response.json().get("error", {}).get("message", "")
    except ValueError:
        raw = ""
    if raw in _ERROR_MESSAGES:
        return _ERROR_MESSAGES[raw]
    if raw.startswith("WEAK_PASSWORD"):
        return "A senha deve ter pelo menos 6 caracteres."
    return "Não foi possível autenticar no provedor de identidade."
