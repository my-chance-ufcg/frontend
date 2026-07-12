import streamlit as st

from src.services.api_client import ApiError, get_recommendations, list_job_invites, list_my_jobs
from src.views.recrutador.painel_vaga import (
    render_confirmed_tab,
    render_job_metrics,
    render_job_selector,
    render_pending_tab,
    render_suggestions_tab,
)

st.title("Painel do Recrutador")

try:
    jobs = list_my_jobs()
except ApiError as error:
    st.error(f"Erro ao consultar vagas: {error}")
    st.stop()

if not jobs:
    st.warning("Nenhuma vaga cadastrada. Crie uma em **Criar Nova Vaga**.")
    st.stop()

vaga_id = render_job_selector(jobs)
if not vaga_id:
    st.stop()

selected_job = next(job for job in jobs if job["vaga_id"] == vaga_id)
st.caption(f"Gerenciando: **{selected_job['titulo']}** (`{vaga_id}`)")

try:
    recommendations = get_recommendations(vaga_id)
except ApiError as error:
    recommendations = []
    st.warning(f"Não foi possível carregar recomendações do NLP: {error}")

try:
    invites = list_job_invites(vaga_id)
except ApiError as error:
    st.error(f"Erro ao consultar convites: {error}")
    st.stop()

pending_invites = [item for item in invites if item["status"] == "ENVIADO"]
confirmed_invites = [item for item in invites if item["status"] == "ACEITO"]

render_job_metrics(recommendations, pending_invites, confirmed_invites)
st.write("---")

if len(jobs) > 1:
    st.info(f"Você possui **{len(jobs)} vagas ativas**. Use o seletor acima para alternar entre elas.")

aba_sugestoes, aba_pendentes, aba_confirmadas = st.tabs(
    ["Sugestões de Matching", "Aguardando Resposta", "Entrevistas Confirmadas"]
)

with aba_sugestoes:
    render_suggestions_tab(vaga_id, recommendations)

with aba_pendentes:
    render_pending_tab(pending_invites)

with aba_confirmadas:
    render_confirmed_tab(confirmed_invites)
