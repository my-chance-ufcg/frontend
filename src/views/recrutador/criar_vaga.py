import streamlit as st

from src.domain.catalog import SKILL_OPTIONS, label_to_skill_key
from src.services.api_client import ApiError, create_job, get_recommendations

st.title("Cadastro de Nova Vaga")
st.markdown("Preencha os dados da vaga conforme o contrato da API do My Chance.")

st.write("---")

st.subheader("1. Informações Básicas")
titulo_vaga = st.text_input("Título da Vaga", placeholder="Desenvolvedor Back-end Pleno")
descricao_vaga = st.text_area(
    "Descrição Técnica",
    height=120,
    placeholder="Responsabilidades, stack principal e contexto da posição...",
)

st.write("---")

st.subheader("2. Orçamento Salarial da Vaga")
salario_maximo = st.number_input(
    "Salário máximo mensal oferecido pela empresa (R$)",
    min_value=1,
    step=100,
    value=8000,
    help="Teto orçamentário da vaga. Candidatos com pretensão acima deste valor são excluídos do matching.",
)

st.write("---")

st.subheader("3. Requisitos Técnicos")
st.caption("Competências obrigatórias exigem nível mínimo. Desejáveis entram no ranking com peso menor.")

skills_obrigatorias = st.multiselect("Competências Obrigatórias", SKILL_OPTIONS)
skills_desejaveis = st.multiselect(
    "Competências Desejáveis",
    [skill for skill in SKILL_OPTIONS if skill not in skills_obrigatorias],
)

st.write("Pesos e níveis mínimos")
requisitos = []
for skill_label in skills_obrigatorias:
    key = label_to_skill_key(skill_label)
    col_peso, col_nivel = st.columns(2)
    with col_peso:
        peso = st.slider(f"Peso — {skill_label}", 1, 5, 5, key=f"peso_obr_{key}")
    with col_nivel:
        nivel_min = st.slider(f"Nível mínimo — {skill_label}", 1, 5, 3, key=f"nivel_obr_{key}")
    requisitos.append(
        {"competencia": key, "peso": peso, "obrigatoria": True, "nivel_min": nivel_min}
    )

for skill_label in skills_desejaveis:
    key = label_to_skill_key(skill_label)
    peso = st.slider(f"Peso (desejável) — {skill_label}", 1, 5, 2, key=f"peso_des_{key}")
    requisitos.append(
        {"competencia": key, "peso": peso, "obrigatoria": False, "nivel_min": 1}
    )

st.write("---")

if st.button("Criar Vaga e Buscar Candidatos", type="primary", use_container_width=True):
    if not titulo_vaga.strip():
        st.error("Informe o título da vaga.")
    elif not skills_obrigatorias:
        st.error("Selecione ao menos uma competência obrigatória.")
    elif salario_maximo <= 0:
        st.error("Informe um orçamento salarial válido.")
    else:
        payload = {
            "titulo": titulo_vaga.strip(),
            "descricao": descricao_vaga.strip() or None,
            "salario_maximo": int(salario_maximo),
            "requisitos": requisitos,
        }

        try:
            created = create_job(payload)
            st.session_state.vaga_id = created["vaga_id"]
            st.success(f"Vaga criada: `{created['vaga_id']}`")

            try:
                recommendations = get_recommendations(created["vaga_id"])
                st.session_state.recommendations = recommendations

                if recommendations:
                    st.subheader("Candidatos sugeridos (motor NLP)")
                    for item in recommendations:
                        score_pct = round(item["compatibilidade_score"] * 100, 1)
                        posicao = item.get("posicao", "?")
                        st.markdown(
                            f"**#{posicao} {item['candidato_id']}** — "
                            f"**{item['compatibilidade']}** ({score_pct}%)"
                        )
                else:
                    st.info("Nenhum candidato compatível encontrado no momento.")
            except ApiError as nlp_error:
                st.warning(
                    f"Vaga criada, mas não foi possível buscar candidatos agora: {nlp_error}. "
                    "Tente novamente no **Painel do Recrutador**."
                )
        except ApiError as error:
            st.error(f"Erro ao criar vaga: {error}")
