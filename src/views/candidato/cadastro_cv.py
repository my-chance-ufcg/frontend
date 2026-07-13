import streamlit as st

from src.domain.catalog import (
    EDUCATION_LEVELS,
    REGIONS,
    ROLE_TITLES,
    SKILL_LABELS,
    label_to_skill_key,
    skill_key_to_label,
)
from src.domain.skill_picker import render_skill_multiselect
from src.domain.user_messages import friendly_error
from src.services.api_client import ApiError, create_profile, get_my_profile, update_profile


def _init_profile_form() -> None:
    if st.session_state.get("_cv_initialized"):
        return

    if "exp_ids" not in st.session_state:
        st.session_state.exp_ids = [0]
        st.session_state.next_id = 1

    if not st.session_state.get("auth_token"):
        st.session_state._cv_initialized = True
        return

    try:
        profile = get_my_profile()
        st.session_state.candidato_id = profile["candidato_id"]
        st.session_state._cv_data = profile

        experiencias = profile.get("experiencias") or []
        if experiencias:
            st.session_state.exp_ids = list(range(len(experiencias)))
            st.session_state.next_id = len(experiencias)
            for index, exp in enumerate(experiencias):
                st.session_state[f"cargo_{index}"] = exp["cargo"]
                st.session_state[f"tempo_{index}"] = exp["tempo_meses"]
        else:
            st.session_state.exp_ids = [0]
            st.session_state.next_id = 1

        for skill_key, level in (profile.get("competencias") or {}).items():
            st.session_state[f"skill_level_{skill_key}"] = level
    except ApiError:
        pass

    st.session_state._cv_initialized = True


_init_profile_form()
cv_data = st.session_state.get("_cv_data", {})


def _render_save_feedback() -> None:
    feedback = st.session_state.get("cv_save_feedback")
    if not feedback:
        return

    if feedback.get("kind") == "created":
        st.success(
            "✅ Seu perfil foi publicado com sucesso! "
            "Agora você pode receber convites de entrevista no **Painel do Candidato**."
        )
    else:
        st.success("✅ Seu currículo foi atualizado com sucesso.")


_render_save_feedback()

st.title("Meu Currículo")

if st.session_state.get("candidato_id"):
    st.caption("Seu perfil está ativo. Recrutadores veem apenas suas competências até você aceitar um convite.")
else:
    st.caption("Preencha os campos abaixo para publicar seu perfil.")

st.warning(
    "Seu nome e contatos **não** aparecem para recrutadores nesta etapa. "
    "Nos projetos, descreva apenas tecnologias — evite links, e-mails ou nomes de empresas."
)

st.write("---")

st.subheader("1. Competências")
st.caption(
    "Selecione suas competências e informe seu nível (0 = sem domínio, 5 = especialista). "
    "Digite no campo para encontrar uma tecnologia."
)

default_skill_labels = [
    SKILL_LABELS[key]
    for key in (cv_data.get("competencias") or {}).keys()
    if key in SKILL_LABELS
]

skills_selecionadas = render_skill_multiselect(
    "Competências:",
    key="cv_skills",
    default=default_skill_labels,
)

competencias: dict[str, int] = {}
if skills_selecionadas:
    with st.container(border=True):
        for skill_label in skills_selecionadas:
            skill_key = label_to_skill_key(skill_label)
            default_level = st.session_state.get(
                f"skill_level_{skill_key}",
                (cv_data.get("competencias") or {}).get(skill_key, 3),
            )
            competencias[skill_key] = st.slider(
                f"Nível em {skill_label}",
                min_value=0,
                max_value=5,
                value=int(default_level),
                key=f"skill_level_{skill_key}",
            )

st.write("---")

st.subheader("2. Informações gerais")
education_keys = [item["key"] for item in EDUCATION_LEVELS]
region_keys = [item["key"] for item in REGIONS]
default_education = cv_data.get("nivel_escolaridade") or education_keys[0]
default_region = cv_data.get("regiao") or region_keys[0]

col_edu, col_reg = st.columns(2)
with col_edu:
    nivel_escolaridade = st.selectbox(
        "Nível de escolaridade",
        options=education_keys,
        index=education_keys.index(default_education) if default_education in education_keys else 0,
        format_func=lambda key: next(item["label"] for item in EDUCATION_LEVELS if item["key"] == key),
    )
with col_reg:
    regiao = st.selectbox(
        "Região",
        options=region_keys,
        index=region_keys.index(default_region) if default_region in region_keys else 0,
        format_func=lambda key: next(item["label"] for item in REGIONS if item["key"] == key),
    )

st.write("---")

st.subheader("3. Pretensão Salarial")
pretensao_minima = st.number_input(
    "Valor mínimo mensal aceitável (R$)",
    min_value=1,
    step=100,
    value=int(cv_data.get("pretensao_salarial_minima") or 3000),
    help="Vagas com salário abaixo deste valor não serão sugeridas a você.",
)

st.write("---")

st.subheader("4. Histórico de Experiências")

experiencias = []
for exp_id in list(st.session_state.exp_ids):
    with st.container(border=True):
        if st.button("✖", key=f"del_{exp_id}", help="Remover experiência"):
            st.session_state.exp_ids.remove(exp_id)
            st.rerun()

        default_cargo = st.session_state.get(f"cargo_{exp_id}", ROLE_TITLES[0])
        default_tempo = int(st.session_state.get(f"tempo_{exp_id}", 12))

        cargo = st.selectbox(
            "Cargo",
            options=ROLE_TITLES,
            index=ROLE_TITLES.index(default_cargo) if default_cargo in ROLE_TITLES else 0,
            key=f"cargo_{exp_id}",
        )
        tempo_meses = st.number_input(
            "Tempo na função (meses)",
            min_value=1,
            step=1,
            value=default_tempo,
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
default_projeto = ""
projetos = cv_data.get("projetos_destaque") or []
if projetos:
    default_projeto = projetos[0]

projeto_destaque = st.text_area(
    "Descreva um projeto significativo (máx. 250 caracteres, foco em tecnologias):",
    value=default_projeto,
    max_chars=250,
    height=120,
)

st.write("---")

button_label = "Salvar alterações" if st.session_state.get("candidato_id") else "Publicar meu perfil"
if st.button(button_label, type="primary", use_container_width=True):
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
            is_update = bool(st.session_state.get("candidato_id"))
            if is_update:
                result = update_profile(payload)
            else:
                result = create_profile(payload)

            st.session_state.candidato_id = result["candidato_id"]
            st.session_state._cv_initialized = False
            st.session_state.cv_save_feedback = {
                "kind": "updated" if is_update else "created",
                "candidato_id": result["candidato_id"],
            }
            st.rerun()
        except ApiError as error:
            st.error(friendly_error(error, "Não foi possível salvar seu perfil. Tente novamente."))
