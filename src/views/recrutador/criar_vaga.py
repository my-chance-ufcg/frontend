import streamlit as st

from src.domain.catalog import label_to_skill_key, skill_key_to_label
from src.domain.skill_picker import render_skill_multiselect
from src.domain.user_messages import friendly_error
from src.services.api_client import ApiError, create_job, get_job, get_recommendations, list_my_jobs, update_job


def _form_scope(editing_job_id: str | None) -> str:
    return editing_job_id or "new"


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


def _load_job_into_session(job_id: str) -> None:
    if st.session_state.get("_job_loaded_id") == job_id:
        return
    try:
        job = get_job(job_id)
        st.session_state._job_form = job
        st.session_state._job_loaded_id = job_id
        _sync_requirement_widget_state(job_id, job)
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


st.title("Gerenciar Vagas")

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

st.markdown("Informe os dados da vaga para publicá-la e encontrar candidatos compatíveis.")
st.write("---")

st.subheader("1. Informações básicas")
titulo_vaga = st.text_input(
    "Título da Vaga",
    value=(job_form or {}).get("titulo", ""),
    placeholder="Desenvolvedor Back-end Pleno",
    key=f"job_titulo_{form_scope}",
)
descricao_vaga = st.text_area(
    "Descrição da vaga",
    value=(job_form or {}).get("descricao") or "",
    height=120,
    placeholder="Responsabilidades, principais tecnologias e contexto da posição...",
    key=f"job_descricao_{form_scope}",
)

st.write("---")

st.subheader("2. Orçamento Salarial da Vaga")
salario_maximo = st.number_input(
    "Salário máximo mensal oferecido pela empresa (R$)",
    min_value=1,
    step=100,
    value=int((job_form or {}).get("salario_maximo") or 8000),
    help="Candidatos com pretensão acima deste valor não serão sugeridos para a vaga.",
    key=f"job_salario_{form_scope}",
)

st.write("---")

st.subheader("3. Competências exigidas")
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
    elif not any(req["obrigatoria"] for req in requisitos):
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
            if editing_job_id:
                update_job(editing_job_id, payload)
                job = get_job(editing_job_id)
                st.session_state.vaga_id = job["vaga_id"]
                st.session_state._job_form = job
                st.session_state._job_loaded_id = editing_job_id
                _sync_requirement_widget_state(editing_job_id, job)
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
            st.rerun()
        except ApiError as error:
            st.error(friendly_error(error, "Não foi possível salvar a vaga."))

_render_job_save_feedback()
