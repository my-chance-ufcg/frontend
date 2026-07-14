from __future__ import annotations

from datetime import date

import streamlit as st

from src.domain.catalog import (
    EDUCATION_LEVELS,
    EMPLOYMENT_TYPES,
    LANGUAGE_LEVELS,
    LANGUAGES,
    MONTH_OPTIONS,
    OUTRO_OPTION,
    ROLE_TITLES,
    SENIORITY_LEVELS,
    SKILL_LABELS,
    STATES,
    STUDY_AREA_OUTRO,
    STUDY_AREAS,
    WORK_MODALITIES,
    catalog_keys,
    catalog_label,
    format_month,
    label_to_skill_key,
)
from src.domain.skill_picker import render_skill_multiselect
from src.domain.user_messages import friendly_error
from src.services.api_client import ApiError, create_profile, get_my_profile, update_profile

CURRENT_YEAR = date.today().year
YEAR_OPTIONS = list(range(CURRENT_YEAR, 1989, -1))
STUDY_OPTION_KEYS = [*catalog_keys(STUDY_AREAS), STUDY_AREA_OUTRO]
PAGE_ID = "cadastro_cv"


def _resolve_study_selection(curso_area: str | None) -> tuple[str | None, str]:
    if not curso_area:
        return None, ""
    if curso_area in catalog_keys(STUDY_AREAS):
        return curso_area, ""
    return STUDY_AREA_OUTRO, curso_area


def _resolve_cargo_selection(cargo: str | None) -> tuple[str, str]:
    if cargo and cargo in ROLE_TITLES and cargo != OUTRO_OPTION:
        return cargo, ""
    if cargo and cargo != OUTRO_OPTION:
        return OUTRO_OPTION, cargo
    return ROLE_TITLES[0], ""


def _sync_profile_widget_state(profile: dict) -> None:
    st.session_state.candidato_id = profile["candidato_id"]
    st.session_state._cv_data = profile

    st.session_state["cv_education"] = profile.get("nivel_escolaridade") or catalog_keys(EDUCATION_LEVELS)[0]
    estado = profile.get("estado")
    st.session_state["cv_estado"] = estado if estado in catalog_keys(STATES) else catalog_keys(STATES)[0]

    study_key, study_outro = _resolve_study_selection(profile.get("curso_area"))
    st.session_state["cv_curso"] = study_key
    st.session_state["cv_curso_outro"] = study_outro

    st.session_state["cv_modalidades"] = [
        key for key in (profile.get("modalidades_preferidas") or []) if key in catalog_keys(WORK_MODALITIES)
    ]
    st.session_state["cv_vinculos"] = [
        key for key in (profile.get("vinculos_preferidos") or []) if key in catalog_keys(EMPLOYMENT_TYPES)
    ]
    pretensao = int(profile.get("pretensao_salarial_minima") or 3000)
    st.session_state["cv_pretensao"] = max(1000, pretensao)
    projetos = profile.get("projetos_destaque") or []
    st.session_state["cv_projeto"] = projetos[0] if projetos else ""

    skill_labels = [
        SKILL_LABELS[key]
        for key in (profile.get("competencias") or {}).keys()
        if key in SKILL_LABELS
    ]
    st.session_state["cv_skills"] = skill_labels
    for skill_key, level in (profile.get("competencias") or {}).items():
        st.session_state[f"skill_level_{skill_key}"] = level

    experiencias = profile.get("experiencias") or []
    if experiencias:
        st.session_state.exp_ids = list(range(len(experiencias)))
        st.session_state.next_id = len(experiencias)
        for index, exp in enumerate(experiencias):
            cargo_choice, cargo_outro = _resolve_cargo_selection(exp.get("cargo"))
            st.session_state[f"cargo_{index}"] = cargo_choice
            st.session_state[f"cargo_outro_{index}"] = cargo_outro
            st.session_state[f"senioridade_{index}"] = exp.get("senioridade") or "junior"
            st.session_state[f"inicio_mes_{index}"] = int(exp.get("inicio_mes") or 1)
            st.session_state[f"inicio_ano_{index}"] = int(exp.get("inicio_ano") or CURRENT_YEAR)
            st.session_state[f"atual_{index}"] = bool(exp.get("atual", False))
            st.session_state[f"fim_mes_{index}"] = int(exp.get("fim_mes") or date.today().month)
            st.session_state[f"fim_ano_{index}"] = int(exp.get("fim_ano") or CURRENT_YEAR)
    else:
        st.session_state.exp_ids = [0]
        st.session_state.next_id = 1

    idiomas = profile.get("idiomas") or []
    if idiomas:
        st.session_state.lang_ids = list(range(len(idiomas)))
        st.session_state.next_lang_id = len(idiomas)
        for index, idioma in enumerate(idiomas):
            idioma_key = idioma.get("idioma") or "portugues"
            if idioma_key not in catalog_keys(LANGUAGES):
                idioma_key = "portugues"
            st.session_state[f"idioma_{index}"] = idioma_key
            st.session_state[f"idioma_nivel_{index}"] = idioma.get("nivel") or "intermediario"
    else:
        st.session_state.lang_ids = [0]
        st.session_state.next_lang_id = 1


def _init_profile_form() -> None:
    # Recarrega da API sempre que o usuário navega de outra página para esta.
    if st.session_state.get("_active_page") != PAGE_ID:
        st.session_state._cv_initialized = False
    st.session_state._active_page = PAGE_ID

    if st.session_state.get("_cv_initialized"):
        return

    if "exp_ids" not in st.session_state:
        st.session_state.exp_ids = [0]
        st.session_state.next_id = 1

    if "lang_ids" not in st.session_state:
        st.session_state.lang_ids = [0]
        st.session_state.next_lang_id = 1

    if not st.session_state.get("auth_token"):
        st.session_state._cv_initialized = True
        return

    try:
        profile = get_my_profile()
        _sync_profile_widget_state(profile)
    except ApiError:
        pass

    st.session_state._cv_initialized = True


_init_profile_form()


def _render_save_feedback() -> None:
    feedback = st.session_state.get("cv_save_feedback")
    if not feedback:
        return

    if feedback.get("kind") == "created":
        st.success(
            "Seu perfil foi publicado com sucesso! "
            "Agora você pode receber convites de entrevista no **Painel do Candidato**."
        )
    else:
        st.success("Seu currículo foi atualizado com sucesso.")


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

skills_selecionadas = render_skill_multiselect(
    "Competências:",
    key="cv_skills",
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
                value=int(st.session_state.get(f"skill_level_{skill_key}", 3)),
                key=f"skill_level_{skill_key}",
            )

st.write("---")

st.subheader("2. Informações gerais")
education_keys = catalog_keys(EDUCATION_LEVELS)
state_keys = catalog_keys(STATES)
modality_keys = catalog_keys(WORK_MODALITIES)
employment_keys = catalog_keys(EMPLOYMENT_TYPES)
language_keys = catalog_keys(LANGUAGES)
language_level_keys = catalog_keys(LANGUAGE_LEVELS)
seniority_keys = catalog_keys(SENIORITY_LEVELS)

col_edu, col_estado = st.columns(2)
with col_edu:
    nivel_escolaridade = st.selectbox(
        "Nível de escolaridade",
        options=education_keys,
        format_func=lambda key: catalog_label(EDUCATION_LEVELS, key),
        key="cv_education",
    )
with col_estado:
    estado = st.selectbox(
        "Estado",
        options=state_keys,
        format_func=lambda key: catalog_label(STATES, key),
        key="cv_estado",
    )

curso_options = [None, *STUDY_OPTION_KEYS]
curso_selecionado = st.selectbox(
    "Área de formação (opcional)",
    options=curso_options,
    format_func=lambda key: (
        "—"
        if key is None
        else "Outro"
        if key == STUDY_AREA_OUTRO
        else catalog_label(STUDY_AREAS, key)
    ),
    key="cv_curso",
)

curso_area: str | None = None
if curso_selecionado == STUDY_AREA_OUTRO:
    curso_outro = st.text_input(
        "Descreva a área de formação",
        max_chars=150,
        key="cv_curso_outro",
        placeholder="Ex.: Design Digital, Física Computacional...",
    )
    curso_area = curso_outro.strip() or None
elif curso_selecionado:
    curso_area = curso_selecionado

modalidades_preferidas = st.multiselect(
    "Modalidades de trabalho preferidas",
    options=modality_keys,
    format_func=lambda key: catalog_label(WORK_MODALITIES, key),
    placeholder="Selecione uma ou mais...",
    key="cv_modalidades",
)

vinculos_preferidos = st.multiselect(
    "Tipos de vínculo preferidos",
    options=employment_keys,
    format_func=lambda key: catalog_label(EMPLOYMENT_TYPES, key),
    placeholder="Selecione um ou mais...",
    key="cv_vinculos",
)

st.write("---")

st.subheader("3. Idiomas")
st.caption("Informe ao menos um idioma e o nível correspondente.")

idiomas: list[dict[str, str]] = []
for lang_id in list(st.session_state.lang_ids):
    with st.container(border=True):
        if st.button("✖", key=f"del_lang_{lang_id}", help="Remover idioma"):
            st.session_state.lang_ids.remove(lang_id)
            st.rerun()

        col_idioma, col_nivel = st.columns(2)
        with col_idioma:
            idioma = st.selectbox(
                "Idioma",
                options=language_keys,
                format_func=lambda key: catalog_label(LANGUAGES, key),
                key=f"idioma_{lang_id}",
            )
        with col_nivel:
            nivel = st.selectbox(
                "Nível",
                options=language_level_keys,
                format_func=lambda key: catalog_label(LANGUAGE_LEVELS, key),
                key=f"idioma_nivel_{lang_id}",
            )
        idiomas.append({"idioma": idioma, "nivel": nivel})

if st.button("➕ Adicionar outro idioma"):
    st.session_state.lang_ids.append(st.session_state.next_lang_id)
    st.session_state.next_lang_id += 1
    st.rerun()

st.write("---")

st.subheader("4. Pretensão Salarial")
pretensao_minima = st.number_input(
    "Valor mínimo mensal aceitável (R$)",
    min_value=1000,
    step=100,
    help="Vagas com salário abaixo deste valor não serão sugeridas a você.",
    key="cv_pretensao",
)

st.write("---")

st.subheader("5. Histórico de Experiências")

experiencias: list[dict] = []
for exp_id in list(st.session_state.exp_ids):
    with st.container(border=True):
        if st.button("✖", key=f"del_{exp_id}", help="Remover experiência"):
            st.session_state.exp_ids.remove(exp_id)
            st.rerun()

        cargo_selecionado = st.selectbox(
            "Cargo",
            options=ROLE_TITLES,
            key=f"cargo_{exp_id}",
        )
        if cargo_selecionado == OUTRO_OPTION:
            cargo_valor = st.text_input(
                "Descreva o cargo",
                max_chars=150,
                key=f"cargo_outro_{exp_id}",
                placeholder="Ex.: Analista de QA, Product Designer...",
            ).strip()
        else:
            cargo_valor = cargo_selecionado

        senioridade = st.selectbox(
            "Senioridade",
            options=seniority_keys,
            format_func=lambda key: catalog_label(SENIORITY_LEVELS, key),
            key=f"senioridade_{exp_id}",
        )

        col_mes, col_ano = st.columns(2)
        with col_mes:
            inicio_mes = st.selectbox(
                "Mês de início",
                options=MONTH_OPTIONS,
                format_func=format_month,
                key=f"inicio_mes_{exp_id}",
            )
        with col_ano:
            inicio_ano = st.selectbox(
                "Ano de início",
                options=YEAR_OPTIONS,
                key=f"inicio_ano_{exp_id}",
            )

        atual = st.checkbox(
            "Trabalho atual",
            key=f"atual_{exp_id}",
        )

        experience_item = {
            "cargo": cargo_valor,
            "senioridade": senioridade,
            "inicio_mes": int(inicio_mes),
            "inicio_ano": int(inicio_ano),
            "atual": atual,
            "fim_mes": None,
            "fim_ano": None,
        }

        if not atual:
            col_fim_mes, col_fim_ano = st.columns(2)
            with col_fim_mes:
                fim_mes = st.selectbox(
                    "Mês de fim",
                    options=MONTH_OPTIONS,
                    format_func=format_month,
                    key=f"fim_mes_{exp_id}",
                )
            with col_fim_ano:
                fim_ano = st.selectbox(
                    "Ano de fim",
                    options=YEAR_OPTIONS,
                    key=f"fim_ano_{exp_id}",
                )
            experience_item["fim_mes"] = int(fim_mes)
            experience_item["fim_ano"] = int(fim_ano)

        if cargo_valor:
            experiencias.append(experience_item)

if st.button("➕ Adicionar outra experiência"):
    st.session_state.exp_ids.append(st.session_state.next_id)
    st.session_state.next_id += 1
    st.rerun()

st.write("---")

st.subheader("6. Projetos de Destaque")
projeto_destaque = st.text_area(
    "Descreva um projeto significativo (máx. 250 caracteres, foco em tecnologias):",
    max_chars=250,
    height=120,
    key="cv_projeto",
)

st.write("---")

button_label = "Salvar alterações" if st.session_state.get("candidato_id") else "Publicar meu perfil"
if st.button(button_label, type="primary", use_container_width=True):
    cargos_incompletos = any(
        (st.session_state.get(f"cargo_{exp_id}") == OUTRO_OPTION)
        and not str(st.session_state.get(f"cargo_outro_{exp_id}") or "").strip()
        for exp_id in st.session_state.exp_ids
    )
    if not competencias:
        st.error("Selecione ao menos uma competência com nível informado.")
    elif curso_selecionado == STUDY_AREA_OUTRO and not curso_area:
        st.error("Descreva a área de formação ou escolha outra opção.")
    elif not modalidades_preferidas:
        st.error("Selecione ao menos uma modalidade de trabalho preferida.")
    elif not vinculos_preferidos:
        st.error("Selecione ao menos um tipo de vínculo preferido.")
    elif not idiomas:
        st.error("Informe ao menos um idioma.")
    elif cargos_incompletos:
        st.error("Preencha a descrição do cargo quando selecionar Outro.")
    elif not experiencias:
        st.error("Informe ao menos uma experiência profissional.")
    elif not str(projeto_destaque or "").strip():
        st.error("Descreva ao menos um projeto de destaque.")
    else:
        payload = {
            "competencias": competencias,
            "experiencias": experiencias,
            "projetos_destaque": [str(projeto_destaque).strip()],
            "nivel_escolaridade": nivel_escolaridade,
            "estado": estado,
            "curso_area": curso_area,
            "pretensao_salarial_minima": int(pretensao_minima),
            "modalidades_preferidas": modalidades_preferidas,
            "vinculos_preferidos": vinculos_preferidos,
            "idiomas": idiomas,
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

_render_save_feedback()
