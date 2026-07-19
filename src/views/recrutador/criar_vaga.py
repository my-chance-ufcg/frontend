from __future__ import annotations

import streamlit as st

from src.domain.catalog import (
    EMPLOYMENT_TYPES,
    LANGUAGE_LEVELS,
    LANGUAGES,
    SENIORITY_LEVELS,
    STATES,
    WORK_MODALITIES,
    catalog_keys,
    catalog_label,
    label_to_skill_key,
)
from src.domain.skill_picker import render_skill_multiselect
from src.domain.user_messages import friendly_error
from src.services.api_client import ApiError, create_job, get_job, get_recommendations, list_my_jobs, update_job
from src.ui.layout import render_page_header


def _form_scope(editing_job_id: str | None) -> str:
    return editing_job_id or "new"


def _ensure_job_lang_state(form_scope: str) -> None:
    ids_key = f"job_lang_ids_{form_scope}"
    next_key = f"job_next_lang_id_{form_scope}"
    if ids_key not in st.session_state:
        st.session_state[ids_key] = [0]
        st.session_state[next_key] = 1


def _sync_language_widget_state(form_scope: str, job_form: dict) -> None:
    idiomas = job_form.get("idiomas") or []
    ids_key = f"job_lang_ids_{form_scope}"
    next_key = f"job_next_lang_id_{form_scope}"

    if idiomas:
        st.session_state[ids_key] = list(range(len(idiomas)))
        st.session_state[next_key] = len(idiomas)
        for index, idioma in enumerate(idiomas):
            st.session_state[f"job_idioma_{index}_{form_scope}"] = idioma.get("idioma") or "portugues"
            st.session_state[f"job_idioma_nivel_{index}_{form_scope}"] = (
                idioma.get("nivel_min") or "basico"
            )
    else:
        st.session_state[ids_key] = [0]
        st.session_state[next_key] = 1


def _sync_requirement_widget_state(form_scope: str, job_form: dict) -> None:
    from src.domain.catalog import SKILL_LABELS

    requisitos = job_form.get("requisitos") or []
    obrigatorias = [req for req in requisitos if req.get("obrigatoria")]
    desejaveis = [req for req in requisitos if not req.get("obrigatoria")]

    default_obr = [SKILL_LABELS[req["competencia"]] for req in obrigatorias if req["competencia"] in SKILL_LABELS]
    default_des = [SKILL_LABELS[req["competencia"]] for req in desejaveis if req["competencia"] in SKILL_LABELS]

    st.session_state[f"job_skills_required_{form_scope}"] = default_obr
    st.session_state[f"job_skills_desired_{form_scope}"] = [
        skill for skill in default_des if skill not in default_obr
    ]

    for req in requisitos:
        skill_key = req["competencia"]
        if req.get("obrigatoria"):
            st.session_state[f"peso_obr_{skill_key}_{form_scope}"] = int(req.get("peso", 5))
            st.session_state[f"nivel_obr_{skill_key}_{form_scope}"] = int(req.get("nivel_min", 3))
        else:
            st.session_state[f"peso_des_{skill_key}_{form_scope}"] = int(req.get("peso", 2))


def _sync_job_form_widget_state(form_scope: str, job_form: dict) -> None:
    st.session_state[f"job_titulo_{form_scope}"] = job_form.get("titulo") or ""
    st.session_state[f"job_empresa_{form_scope}"] = job_form.get("empresa_instituicao") or ""
    st.session_state[f"job_descricao_{form_scope}"] = job_form.get("descricao") or ""
    st.session_state[f"job_modalidade_{form_scope}"] = job_form.get("modalidade") or "remoto"
    st.session_state[f"job_vinculo_{form_scope}"] = job_form.get("tipo_vinculo") or "clt"
    local = job_form.get("local")
    st.session_state[f"job_local_{form_scope}"] = local if local in catalog_keys(STATES) else None
    st.session_state[f"job_senioridade_{form_scope}"] = job_form.get("senioridade") or "pleno"
    st.session_state[f"job_salario_min_{form_scope}"] = int(job_form.get("salario_minimo") or 0)
    st.session_state[f"job_salario_{form_scope}"] = int(job_form.get("salario_maximo") or 8000)
    _sync_requirement_widget_state(form_scope, job_form)
    _sync_language_widget_state(form_scope, job_form)


def _load_job_into_session(job_id: str) -> None:
    if st.session_state.get("_job_loaded_id") == job_id:
        return
    try:
        job = get_job(job_id)
        st.session_state._job_form = job
        st.session_state._job_loaded_id = job_id
        _sync_job_form_widget_state(job_id, job)
    except ApiError as error:
        st.error(friendly_error(error, "Não foi possível carregar os dados da vaga."))


def _render_requirement_fields(job_form: dict | None, form_scope: str) -> list[dict]:
    requisitos = (job_form or {}).get("requisitos") or []
    obrigatorias = [req for req in requisitos if req.get("obrigatoria")]
    desejaveis = [req for req in requisitos if not req.get("obrigatoria")]

    from src.domain.catalog import SKILL_LABELS

    default_obr = [SKILL_LABELS[req["competencia"]] for req in obrigatorias if req["competencia"] in SKILL_LABELS]
    default_des = [SKILL_LABELS[req["competencia"]] for req in desejaveis if req["competencia"] in SKILL_LABELS]

    skills_obrigatorias = render_skill_multiselect(
        "Competências Obrigatórias",
        key=f"job_skills_required_{form_scope}",
        default=default_obr,
    )
    skills_desejaveis = render_skill_multiselect(
        "Competências Desejáveis",
        key=f"job_skills_desired_{form_scope}",
        default=[skill for skill in default_des if skill not in skills_obrigatorias],
        exclude_labels=skills_obrigatorias,
    )

    req_map = {req["competencia"]: req for req in requisitos}
    result = []

    if skills_obrigatorias or skills_desejaveis:
        st.write("Importância e nível mínimo exigido")

    for skill_label in skills_obrigatorias:
        key = label_to_skill_key(skill_label)
        existing = req_map.get(key, {})
        col_peso, col_nivel = st.columns(2)
        with col_peso:
            peso = st.slider(
                f"Importância — {skill_label}",
                1,
                5,
                int(existing.get("peso", 5)),
                key=f"peso_obr_{key}_{form_scope}",
            )
        with col_nivel:
            nivel_min = st.slider(
                f"Nível mínimo — {skill_label}",
                1,
                5,
                int(existing.get("nivel_min", 3)),
                key=f"nivel_obr_{key}_{form_scope}",
            )
        result.append({"competencia": key, "peso": peso, "obrigatoria": True, "nivel_min": nivel_min})

    for skill_label in skills_desejaveis:
        key = label_to_skill_key(skill_label)
        existing = req_map.get(key, {})
        peso = st.slider(
            f"Importância (desejável) — {skill_label}",
            1,
            5,
            int(existing.get("peso", 2)),
            key=f"peso_des_{key}_{form_scope}",
        )
        result.append({"competencia": key, "peso": peso, "obrigatoria": False, "nivel_min": 1})

    return result


def _render_language_fields(form_scope: str) -> list[dict[str, str]]:
    _ensure_job_lang_state(form_scope)
    language_keys = catalog_keys(LANGUAGES)
    language_level_keys = catalog_keys(LANGUAGE_LEVELS)
    ids_key = f"job_lang_ids_{form_scope}"
    next_key = f"job_next_lang_id_{form_scope}"

    idiomas: list[dict[str, str]] = []
    for lang_id in list(st.session_state[ids_key]):
        with st.container(border=True):
            if st.button("✖", key=f"del_job_lang_{lang_id}_{form_scope}", help="Remover idioma"):
                st.session_state[ids_key].remove(lang_id)
                st.rerun()

            default_idioma = st.session_state.get(
                f"job_idioma_{lang_id}_{form_scope}", "portugues"
            )
            default_nivel = st.session_state.get(
                f"job_idioma_nivel_{lang_id}_{form_scope}", "basico"
            )

            col_idioma, col_nivel = st.columns(2)
            with col_idioma:
                idioma = st.selectbox(
                    "Idioma",
                    options=language_keys,
                    index=language_keys.index(default_idioma) if default_idioma in language_keys else 0,
                    format_func=lambda key: catalog_label(LANGUAGES, key),
                    key=f"job_idioma_{lang_id}_{form_scope}",
                )
            with col_nivel:
                nivel_min = st.selectbox(
                    "Nível mínimo",
                    options=language_level_keys,
                    index=(
                        language_level_keys.index(default_nivel)
                        if default_nivel in language_level_keys
                        else 0
                    ),
                    format_func=lambda key: catalog_label(LANGUAGE_LEVELS, key),
                    key=f"job_idioma_nivel_{lang_id}_{form_scope}",
                )
            idiomas.append({"idioma": idioma, "nivel_min": nivel_min})

    if st.button("➕ Adicionar outro idioma", key=f"add_job_lang_{form_scope}"):
        st.session_state[ids_key].append(st.session_state[next_key])
        st.session_state[next_key] += 1
        st.rerun()

    return idiomas


def _render_job_save_feedback() -> None:
    feedback = st.session_state.get("job_save_feedback")
    if not feedback:
        return

    if feedback.get("kind") == "created":
        st.success("Vaga criada com sucesso!")
    else:
        st.success("Vaga atualizada com sucesso!")

    if feedback.get("recommendations_warning"):
        st.warning(
            "Vaga criada, mas não foi possível carregar candidatos sugeridos agora. "
            "Confira no **Painel do Recrutador**."
        )
        return

    recommendations = feedback.get("recommendations") or []
    if recommendations:
        st.subheader("Candidatos sugeridos")
        for item in recommendations:
            score_pct = round(item["compatibilidade_score"] * 100, 1)
            posicao = item.get("posicao", "?")
            st.markdown(
                f"**#{posicao} Perfil {item['candidato_id']}** — "
                f"**{item['compatibilidade']}** ({score_pct}%)"
            )
    elif feedback.get("kind") == "created":
        st.info("Nenhum candidato compatível encontrado no momento.")


render_page_header(
    title="Publicar vaga",
    eyebrow="Gestão de oportunidades",
    subtitle="Informe os dados da vaga para publicá-la e encontrar candidatos compatíveis.",
)

modo = st.radio("Ação", ["Criar nova vaga", "Editar vaga existente"], horizontal=True)

job_form: dict | None = None
editing_job_id: str | None = None
form_scope = "new"

if modo == "Editar vaga existente":
    try:
        jobs = list_my_jobs()
    except ApiError as error:
        st.error(friendly_error(error, "Não foi possível listar suas vagas."))
        st.stop()

    if not jobs:
        st.warning("Nenhuma vaga cadastrada para editar.")
        st.stop()

    options = {job["vaga_id"]: job["titulo"] for job in jobs}
    editing_job_id = st.selectbox(
        "Selecione a vaga",
        options=list(options.keys()),
        format_func=lambda job_id: options[job_id],
    )
    form_scope = _form_scope(editing_job_id)
    _load_job_into_session(editing_job_id)
    job_form = st.session_state.get("_job_form")
else:
    st.session_state.pop("_job_loaded_id", None)
    if f"job_modalidade_{form_scope}" not in st.session_state:
        st.session_state[f"job_modalidade_{form_scope}"] = "remoto"
        st.session_state[f"job_vinculo_{form_scope}"] = "clt"
        st.session_state[f"job_senioridade_{form_scope}"] = "pleno"
        st.session_state[f"job_salario_min_{form_scope}"] = 0
        st.session_state[f"job_salario_{form_scope}"] = 8000

_ensure_job_lang_state(form_scope)

modality_keys = catalog_keys(WORK_MODALITIES)
employment_keys = catalog_keys(EMPLOYMENT_TYPES)
seniority_keys = catalog_keys(SENIORITY_LEVELS)
state_keys = catalog_keys(STATES)

st.write("---")

st.subheader("1. Informações básicas")
titulo_vaga = st.text_input(
    "Título da Vaga",
    placeholder="Desenvolvedor Back-end Pleno",
    key=f"job_titulo_{form_scope}",
)
empresa_instituicao = st.text_input(
    "Empresa ou instituição",
    placeholder="Nome da empresa ou instituição",
    key=f"job_empresa_{form_scope}",
)
descricao_vaga = st.text_area(
    "Descrição da vaga",
    height=120,
    placeholder="Responsabilidades, principais tecnologias e contexto da posição...",
    key=f"job_descricao_{form_scope}",
)

col_mod, col_vinculo = st.columns(2)
with col_mod:
    modalidade = st.selectbox(
        "Modalidade",
        options=modality_keys,
        format_func=lambda key: catalog_label(WORK_MODALITIES, key),
        key=f"job_modalidade_{form_scope}",
    )
with col_vinculo:
    tipo_vinculo = st.selectbox(
        "Tipo de vínculo",
        options=employment_keys,
        format_func=lambda key: catalog_label(EMPLOYMENT_TYPES, key),
        key=f"job_vinculo_{form_scope}",
    )

col_local, col_senioridade = st.columns(2)
with col_local:
    local = st.selectbox(
        "Estado (obrigatório para presencial)",
        options=[None, *state_keys],
        format_func=lambda key: "—" if key is None else catalog_label(STATES, key),
        key=f"job_local_{form_scope}",
        help="Usado para filtrar candidatos em vagas presenciais.",
    )
with col_senioridade:
    senioridade = st.selectbox(
        "Senioridade",
        options=seniority_keys,
        format_func=lambda key: catalog_label(SENIORITY_LEVELS, key),
        key=f"job_senioridade_{form_scope}",
    )

st.write("---")

st.subheader("2. Orçamento salarial")
col_min, col_max = st.columns(2)
with col_min:
    salario_minimo_raw = st.number_input(
        "Salário mínimo mensal (R$) — opcional",
        min_value=0,
        step=100,
        help="Deixe 0 se não houver salário mínimo definido.",
        key=f"job_salario_min_{form_scope}",
    )
with col_max:
    salario_maximo = st.number_input(
        "Salário máximo mensal oferecido (R$)",
        min_value=1,
        step=100,
        help="Candidatos com pretensão acima deste valor não serão sugeridos para a vaga.",
        key=f"job_salario_{form_scope}",
    )

st.write("---")

st.subheader("3. Idiomas exigidos")
st.caption("Opcional. Informe idiomas e o nível mínimo esperado para a vaga.")
idiomas = _render_language_fields(form_scope)

st.write("---")

st.subheader("4. Competências exigidas")
st.caption(
    "Marque as competências obrigatórias e informe o nível mínimo esperado. "
    "As desejáveis ajudam a priorizar candidatos, mas não são eliminatórias."
)
requisitos = _render_requirement_fields(job_form, form_scope)

st.write("---")

submit_label = "Salvar alterações" if editing_job_id else "Criar Vaga e Buscar Candidatos"
if st.button(submit_label, type="primary", use_container_width=True):
    if not titulo_vaga.strip():
        st.error("Informe o título da vaga.")
    elif not empresa_instituicao.strip():
        st.error("Informe a empresa ou instituição.")
    elif modalidade == "presencial" and not local:
        st.error("Informe o estado para vagas presenciais.")
    elif not any(req["obrigatoria"] for req in requisitos):
        st.error("Selecione ao menos uma competência obrigatória.")
    elif salario_maximo <= 0:
        st.error("Informe um orçamento salarial válido.")
    elif salario_minimo_raw > 0 and salario_minimo_raw > salario_maximo:
        st.error("O salário mínimo não pode ser maior que o salário máximo.")
    else:
        payload = {
            "titulo": titulo_vaga.strip(),
            "descricao": descricao_vaga.strip() or None,
            "empresa_instituicao": empresa_instituicao.strip(),
            "modalidade": modalidade,
            "tipo_vinculo": tipo_vinculo,
            "local": local,
            "senioridade": senioridade,
            "salario_minimo": int(salario_minimo_raw) if salario_minimo_raw > 0 else None,
            "salario_maximo": int(salario_maximo),
            "requisitos": requisitos,
            "idiomas": idiomas,
        }

        try:
            if editing_job_id:
                update_job(editing_job_id, payload)
                job = get_job(editing_job_id)
                st.session_state.vaga_id = job["vaga_id"]
                st.session_state._job_form = job
                st.session_state._job_loaded_id = editing_job_id
                _sync_job_form_widget_state(editing_job_id, job)
                st.session_state.job_save_feedback = {"kind": "updated"}
            else:
                created = create_job(payload)
                st.session_state.vaga_id = created["vaga_id"]
                feedback: dict = {"kind": "created"}
                try:
                    recommendations = get_recommendations(st.session_state.vaga_id)
                    feedback["recommendations"] = recommendations
                except ApiError:
                    feedback["recommendations_warning"] = True
                st.session_state.job_save_feedback = feedback
                # Keep create form values until user switches to edit
            st.rerun()
        except ApiError as error:
            st.error(friendly_error(error, "Não foi possível salvar a vaga."))

_render_job_save_feedback()
