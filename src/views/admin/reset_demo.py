import streamlit as st

from src.domain.user_messages import friendly_error
from src.services.api_client import ApiError, reset_demo_data
from src.ui.layout import render_page_header

SCENARIOS = [
    {
        "id": "base",
        "title": "Estado base",
        "login": "Contas demo sem convites",
        "use_for": "C1 (cadastro novo) e R2 (criar vaga do zero)",
        "details": [
            "Recrutadores e candidatos `*@demo.local` com perfis e vagas",
            "Sem convites — ambiente limpo para cadastro ou criação de vaga",
            "Opção R2: `recruiter.teste@demo.local` / `recruiter123` (sem vagas)",
        ],
    },
    {
        "id": "r1",
        "title": "Cenário R1 — Recrutador",
        "login": "recruiter@mychance.local / recruiter123",
        "use_for": "Fluxo completo com convites em andamento",
        "details": [
            "Ana aceita + horário proposto (Entrevistas confirmadas)",
            "Diego aguardando resposta",
            "Elisa recusou (seção no ranking)",
        ],
    },
    {
        "id": "c2",
        "title": "Cenário C2 — Candidato",
        "login": "ana.silva@demo.local / candidato123",
        "use_for": "Convites, recusa, aceite e agendamento",
        "details": [
            "Estágio em Dados e Frontend React pendentes (recusar e aceitar na sessão)",
            "Backend Python aceito com horário proposto (agendamento)",
        ],
    },
]

render_page_header(
    title="Preparar ambiente de testes",
    eyebrow="Administração",
    subtitle="Escolha o preset do cenário antes de cada sessão. Todos os dados atuais serão substituídos.",
)

st.warning(
    "Cada opção apaga **todos** os dados atuais (incluindo contas criadas durante testes) "
    "e recria o conjunto correspondente ao cenário."
)

confirmed = st.checkbox("Entendo que todos os dados serão apagados e recriados.")

for scenario in SCENARIOS:
    with st.container(border=True):
        st.markdown(f"**{scenario['title']}**")
        st.caption(f"Participante entra com: {scenario['login']}")
        st.markdown(f"*{scenario['use_for']}*")
        for detail in scenario["details"]:
            st.markdown(f"- {detail}")

        if st.button(
            f"Preparar {scenario['title']}",
            key=f"reset_{scenario['id']}",
            type="primary" if scenario["id"] != "base" else "secondary",
            disabled=not confirmed,
            use_container_width=True,
        ):
            try:
                result = reset_demo_data(scenario["id"])
                st.success(result.get("message", "Ambiente preparado com sucesso."))
            except ApiError as error:
                st.error(friendly_error(error, "Não foi possível preparar o ambiente de testes."))
