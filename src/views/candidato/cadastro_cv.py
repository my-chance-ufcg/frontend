import streamlit as st

from src.domain.catalog import (
    EDUCATION_LEVELS,
    REGIONS,
    ROLE_TITLES,
    SKILL_OPTIONS,
    label_to_skill_key,
)
from src.services.api_client import ApiError, create_profile, update_profile

st.title("Cadastro de Perfil Profissional")

st.warning(
    "⚠️ **Atenção:** Seu perfil é estritamente anônimo. "
    "Descreva apenas tecnologias nos projetos — sem links, e-mails ou nomes identificáveis."
)

st.write("---")

st.subheader("1. Competências Técnicas")
st.caption("Selecione as skills relevantes e informe seu nível de proficiência (0 = sem domínio, 5 = especialista).")

skills_selecionadas = st.multiselect(
    "Competências:",
    options=SKILL_OPTIONS,
    help="Somente competências do vocabulário fechado do My Chance.",
)

competencias: dict[str, int] = {}
if skills_selecionadas:
    with st.container(border=True):
        for skill_label in skills_selecionadas:
            skill_key = label_to_skill_key(skill_label)
            competencias[skill_key] = st.slider(
                f"Nível em {skill_label}",
                min_value=0,
                max_value=5,
                value=3,
                key=f"skill_level_{skill_key}",
            )

st.write("---")

st.subheader("2. Metadados Anonimizados")
col_edu, col_reg = st.columns(2)
with col_edu:
    nivel_escolaridade = st.selectbox(
        "Nível de escolaridade",
        options=[item["key"] for item in EDUCATION_LEVELS],
        format_func=lambda key: next(item["label"] for item in EDUCATION_LEVELS if item["key"] == key),
    )
with col_reg:
    regiao = st.selectbox(
        "Região (para logística de contratação)",
        options=[item["key"] for item in REGIONS],
        format_func=lambda key: next(item["label"] for item in REGIONS if item["key"] == key),
    )

st.write("---")

st.subheader("3. Pretensão Salarial")
pretensao_minima = st.number_input(
    "Valor mínimo mensal aceitável (R$)",
    min_value=1,
    step=100,
    value=3000,
    help="Sua pretensão salarial mínima. Vagas com orçamento inferior serão desconsideradas no matching.",
)

st.write("---")

st.subheader("4. Histórico de Experiências")

if "exp_ids" not in st.session_state:
    st.session_state.exp_ids = [0]
    st.session_state.next_id = 1

experiencias = []
for exp_id in list(st.session_state.exp_ids):
    with st.container(border=True):
        if st.button("✖", key=f"del_{exp_id}", help="Remover experiência"):
            st.session_state.exp_ids.remove(exp_id)
            st.rerun()

        cargo = st.selectbox(
            "Cargo normalizado",
            options=ROLE_TITLES,
            key=f"cargo_{exp_id}",
        )
        tempo_meses = st.number_input(
            "Tempo na função (meses)",
            min_value=1,
            step=1,
            key=f"tempo_{exp_id}",
        )
        if tempo_meses >= 1:
            experiencias.append({"cargo": cargo, "tempo_meses": int(tempo_meses)})

if st.button("➕ Adicionar outra experiência"):
    st.session_state.exp_ids.append(st.session_state.next_id)
    st.session_state.next_id += 1
    st.rerun()

st.write("---")

st.subheader("5. Projetos de Destaque")
projeto_destaque = st.text_area(
    "Descreva um projeto significativo (máx. 250 caracteres, foco em tecnologias):",
    max_chars=250,
    height=120,
)

st.write("---")

if st.button("Finalizar e Publicar Perfil Anônimo", type="primary", use_container_width=True):
    if not competencias:
        st.error("Selecione ao menos uma competência com nível informado.")
    elif not experiencias:
        st.error("Informe ao menos uma experiência com tempo em meses.")
    elif not projeto_destaque.strip():
        st.error("Descreva ao menos um projeto de destaque.")
    else:
        payload = {
            "competencias": competencias,
            "experiencias": experiencias,
            "projetos_destaque": [projeto_destaque.strip()],
            "nivel_escolaridade": nivel_escolaridade,
            "regiao": regiao,
            "pretensao_salarial_minima": int(pretensao_minima),
        }

        try:
            if st.session_state.get("candidato_id"):
                result = update_profile(st.session_state.candidato_id, payload)
            else:
                result = create_profile(payload)
                st.session_state.candidato_id = result["candidato_id"]

            st.success(f"✅ Perfil salvo. ID anônimo: `{result['candidato_id']}`")
        except ApiError as error:
            st.error(f"Não foi possível salvar o perfil: {error}")

if st.session_state.get("candidato_id"):
    st.info(f"Perfil ativo: `{st.session_state.candidato_id}`")
