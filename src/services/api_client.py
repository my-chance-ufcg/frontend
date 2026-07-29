from __future__ import annotations

from typing import Any

import requests
import streamlit as st

from src.config import API_BASE_URL


class ApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _auth_headers() -> dict[str, str]:
    token = st.session_state.get("auth_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def _handle_response(response: requests.Response) -> Any:
    if response.ok:
        if not response.content:
            return None
        return response.json()

    detail = response.text
    try:
        payload = response.json()
        if isinstance(payload, dict):
            detail = payload.get("detail", payload.get("title", detail))
    except ValueError:
        pass
    raise ApiError(str(detail), response.status_code)


def register(payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/auth/register",
        json=payload,
        timeout=20,
    )
    return _handle_response(response)


def login(payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/auth/login",
        json=payload,
        timeout=20,
    )
    return _handle_response(response)


def get_current_user() -> dict[str, Any]:
    response = requests.get(
        f"{API_BASE_URL}/api/v1/auth/me",
        headers=_auth_headers(),
        timeout=20,
    )
    return _handle_response(response)


def create_profile(payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/candidates/profiles",
        json=payload,
        headers=_auth_headers(),
        timeout=20,
    )
    return _handle_response(response)


def update_profile(payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.put(
        f"{API_BASE_URL}/api/v1/candidates/profiles/me",
        json=payload,
        headers=_auth_headers(),
        timeout=20,
    )
    return _handle_response(response)


def get_my_profile() -> dict[str, Any]:
    response = requests.get(
        f"{API_BASE_URL}/api/v1/candidates/me/profile",
        headers=_auth_headers(),
        timeout=20,
    )
    return _handle_response(response)


def create_job(payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/jobs",
        json=payload,
        headers=_auth_headers(),
        timeout=20,
    )
    return _handle_response(response)


def list_my_jobs() -> list[dict[str, Any]]:
    response = requests.get(
        f"{API_BASE_URL}/api/v1/jobs/mine",
        headers=_auth_headers(),
        timeout=20,
    )
    return _handle_response(response)


def get_recommendations(job_id: str) -> list[dict[str, Any]]:
    response = requests.get(
        f"{API_BASE_URL}/api/v1/jobs/{job_id}/recommendations",
        headers=_auth_headers(),
        timeout=30,
    )
    return _handle_response(response)


def send_invite(job_id: str, candidato_id: str, mensagem: str) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/jobs/{job_id}/invites",
        json={"candidato_id": candidato_id, "mensagem": mensagem},
        headers=_auth_headers(),
        timeout=20,
    )
    return _handle_response(response)


def list_my_invites() -> list[dict[str, Any]]:
    response = requests.get(
        f"{API_BASE_URL}/api/v1/candidates/me/invites",
        headers=_auth_headers(),
        timeout=20,
    )
    return _handle_response(response)


def accept_invite(invite_id: str) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/invites/{invite_id}/accept",
        headers=_auth_headers(),
        timeout=20,
    )
    return _handle_response(response)


def reject_invite(invite_id: str) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/invites/{invite_id}/reject",
        headers=_auth_headers(),
        timeout=20,
    )
    return _handle_response(response)


def list_job_invites(job_id: str) -> list[dict[str, Any]]:
    response = requests.get(
        f"{API_BASE_URL}/api/v1/jobs/{job_id}/invites",
        headers=_auth_headers(),
        timeout=20,
    )
    return _handle_response(response)


def schedule_interview(invite_id: str, proposed_at: str, meeting_link: str | None) -> dict[str, Any]:
    payload: dict[str, Any] = {"proposed_interview_at": proposed_at}
    if meeting_link:
        payload["meeting_link"] = meeting_link
    response = requests.post(
        f"{API_BASE_URL}/api/v1/invites/{invite_id}/schedule",
        json=payload,
        headers=_auth_headers(),
        timeout=20,
    )
    return _handle_response(response)


def confirm_schedule(invite_id: str) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/invites/{invite_id}/schedule/confirm",
        headers=_auth_headers(),
        timeout=20,
    )
    return _handle_response(response)


def counter_propose_schedule(
    invite_id: str, proposed_at: str, meeting_link: str | None
) -> dict[str, Any]:
    payload: dict[str, Any] = {"proposed_interview_at": proposed_at}
    if meeting_link:
        payload["meeting_link"] = meeting_link
    response = requests.post(
        f"{API_BASE_URL}/api/v1/invites/{invite_id}/schedule/counter-propose",
        json=payload,
        headers=_auth_headers(),
        timeout=20,
    )
    return _handle_response(response)


def get_job(job_id: str) -> dict[str, Any]:
    response = requests.get(
        f"{API_BASE_URL}/api/v1/jobs/{job_id}",
        headers=_auth_headers(),
        timeout=20,
    )
    return _handle_response(response)


def update_job(job_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.put(
        f"{API_BASE_URL}/api/v1/jobs/{job_id}",
        json=payload,
        headers=_auth_headers(),
        timeout=20,
    )
    return _handle_response(response)


def reset_demo_data(scenario: str = "base") -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/admin/reset",
        params={"scenario": scenario},
        headers=_auth_headers(),
        timeout=60,
    )
    return _handle_response(response)
