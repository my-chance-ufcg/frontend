from __future__ import annotations

from src.services.api_client import ApiError


def friendly_error(error: Exception, fallback: str) -> str:
    if isinstance(error, ApiError) and error.status_code == 401:
        return "E-mail ou senha incorretos. Tente novamente."
    if isinstance(error, ApiError) and error.status_code >= 500:
        return "O serviço está temporariamente indisponível. Tente novamente em instantes."
    return fallback
