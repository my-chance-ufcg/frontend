from __future__ import annotations

from typing import Any

import requests

from src.config import API_BASE_URL, DEFAULT_RECRUITER_ID


class ApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _handle_response(response: requests.Response) -> Any:
    if response.ok:
        if not response.content:
            return None
        return response.json()

    detail = response.text
    try:
        payload = response.json()
        detail = payload.get("detail", detail)
    except ValueError:
        pass
    raise ApiError(str(detail), response.status_code)


def create_profile(payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/candidates/profiles",
        json=payload,
        timeout=20,
    )
    return _handle_response(response)


def update_profile(candidato_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.put(
        f"{API_BASE_URL}/api/v1/candidates/profiles/{candidato_id}",
        json=payload,
        timeout=20,
    )
    return _handle_response(response)


def create_job(payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/jobs",
        json=payload,
        timeout=20,
    )
    return _handle_response(response)


def get_recommendations(job_id: str) -> list[dict[str, Any]]:
    response = requests.get(
        f"{API_BASE_URL}/api/v1/jobs/{job_id}/recommendations",
        timeout=30,
    )
    return _handle_response(response)


def send_invite(job_id: str, candidato_id: str, mensagem: str) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/jobs/{job_id}/invites",
        json={"candidato_id": candidato_id, "mensagem": mensagem},
        timeout=20,
    )
    return _handle_response(response)


def list_candidate_invites(candidato_id: str) -> list[dict[str, Any]]:
    response = requests.get(
        f"{API_BASE_URL}/api/v1/candidates/{candidato_id}/invites",
        timeout=20,
    )
    return _handle_response(response)


def accept_invite(invite_id: str) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/invites/{invite_id}/accept",
        timeout=20,
    )
    return _handle_response(response)


def reject_invite(invite_id: str) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/invites/{invite_id}/reject",
        timeout=20,
    )
    return _handle_response(response)


def list_job_invites(job_id: str) -> list[dict[str, Any]]:
    response = requests.get(
        f"{API_BASE_URL}/api/v1/jobs/{job_id}/invites",
        timeout=20,
    )
    return _handle_response(response)


def get_sample_job_id() -> str | None:
    response = requests.get(
        f"{API_BASE_URL}/api/v1/dev/sample-job-id",
        timeout=10,
    )
    payload = _handle_response(response)
    return payload.get("job_id") if payload else None


def default_recruiter_id() -> str:
    return DEFAULT_RECRUITER_ID
