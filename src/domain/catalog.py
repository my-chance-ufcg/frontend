from __future__ import annotations

SKILLS = [
    {"key": "python", "label": "Python"},
    {"key": "javascript", "label": "JavaScript"},
    {"key": "typescript", "label": "TypeScript"},
    {"key": "java", "label": "Java"},
    {"key": "kotlin", "label": "Kotlin"},
    {"key": "go", "label": "Go"},
    {"key": "csharp", "label": "C#"},
    {"key": "sql", "label": "SQL"},
    {"key": "postgresql", "label": "PostgreSQL"},
    {"key": "mongodb", "label": "MongoDB"},
    {"key": "redis", "label": "Redis"},
    {"key": "react", "label": "React"},
    {"key": "angular", "label": "Angular"},
    {"key": "vue", "label": "Vue"},
    {"key": "nodejs", "label": "Node.js"},
    {"key": "spring", "label": "Spring Boot"},
    {"key": "django", "label": "Django"},
    {"key": "fastapi", "label": "FastAPI"},
    {"key": "rest_api", "label": "REST API"},
    {"key": "graphql", "label": "GraphQL"},
    {"key": "docker", "label": "Docker"},
    {"key": "kubernetes", "label": "Kubernetes"},
    {"key": "terraform", "label": "Terraform"},
    {"key": "cicd", "label": "CI/CD"},
    {"key": "aws", "label": "AWS"},
    {"key": "azure", "label": "Azure"},
    {"key": "linux", "label": "Linux"},
    {"key": "git", "label": "Git"},
    {"key": "kafka", "label": "Apache Kafka"},
    {"key": "powerbi", "label": "Power BI"},
    {"key": "streamlit", "label": "Streamlit"},
    {"key": "machine_learning", "label": "Machine Learning"},
    {"key": "data_analysis", "label": "Análise de Dados"},
    {"key": "agile", "label": "Metodologias Ágeis"},
]

SKILL_LABELS = {item["key"]: item["label"] for item in SKILLS}
SKILL_OPTIONS = [item["label"] for item in SKILLS]

EDUCATION_LEVELS = [
    {"key": "ensino_medio_completo", "label": "Ensino Médio Completo"},
    {"key": "tecnico", "label": "Ensino Técnico"},
    {"key": "graduacao_andamento", "label": "Graduação em Andamento"},
    {"key": "graduacao_concluida", "label": "Graduação Concluída"},
    {"key": "pos_graduacao_andamento", "label": "Pós-Graduação em Andamento"},
    {"key": "pos_graduacao_concluida", "label": "Pós-Graduação Concluída"},
]

REGIONS = [
    {"key": "ac", "label": "Acre"},
    {"key": "al", "label": "Alagoas"},
    {"key": "ap", "label": "Amapá"},
    {"key": "am", "label": "Amazonas"},
    {"key": "ba", "label": "Bahia"},
    {"key": "ce", "label": "Ceará"},
    {"key": "df", "label": "Distrito Federal"},
    {"key": "es", "label": "Espírito Santo"},
    {"key": "go", "label": "Goiás"},
    {"key": "ma", "label": "Maranhão"},
    {"key": "mt", "label": "Mato Grosso"},
    {"key": "ms", "label": "Mato Grosso do Sul"},
    {"key": "mg", "label": "Minas Gerais"},
    {"key": "pa", "label": "Pará"},
    {"key": "pb", "label": "Paraíba"},
    {"key": "pr", "label": "Paraná"},
    {"key": "pe", "label": "Pernambuco"},
    {"key": "pi", "label": "Piauí"},
    {"key": "rj", "label": "Rio de Janeiro"},
    {"key": "rn", "label": "Rio Grande do Norte"},
    {"key": "rs", "label": "Rio Grande do Sul"},
    {"key": "ro", "label": "Rondônia"},
    {"key": "rr", "label": "Roraima"},
    {"key": "sc", "label": "Santa Catarina"},
    {"key": "sp", "label": "São Paulo"},
    {"key": "se", "label": "Sergipe"},
    {"key": "to", "label": "Tocantins"},
]

# Alias semântico: o campo de localização do candidato/vaga é o Estado (UF).
STATES = REGIONS

ROLE_TITLES = [
    "Desenvolvedor Backend",
    "Desenvolvedor Frontend",
    "Desenvolvedor Full Stack",
    "Analista de Dados",
    "Engenheiro de Dados",
    "Cientista de Dados",
    "Engenheiro de Software",
    "DevOps / SRE",
    "Analista de Sistemas",
    "Pesquisador",
    "Outro",
]

OUTRO_OPTION = "Outro"

INVITE_STATUS_LABELS = {
    "ENVIADO": "Aguardando sua resposta",
    "ACEITO": "Aceito — dados autorizados",
    "RECUSADO": "Recusado",
    "INVALIDADO": "Invalidado",
    "SUGERIDO": "Sugerido",
}

WORK_MODALITIES = [
    {"key": "remoto", "label": "Remoto"},
    {"key": "hibrido", "label": "Híbrido"},
    {"key": "presencial", "label": "Presencial"},
]

EMPLOYMENT_TYPES = [
    {"key": "bolsa_projeto", "label": "Bolsa / projeto acadêmico"},
    {"key": "estagio", "label": "Estágio"},
    {"key": "clt", "label": "CLT"},
    {"key": "pj", "label": "PJ"},
    {"key": "freelancer", "label": "Freelancer"},
]

SENIORITY_LEVELS = [
    {"key": "bolsa_iniciacao", "label": "Bolsa / Iniciação"},
    {"key": "estagio", "label": "Estágio"},
    {"key": "junior", "label": "Júnior"},
    {"key": "pleno", "label": "Pleno"},
    {"key": "senior", "label": "Sênior"},
    {"key": "especialista", "label": "Especialista"},
]

LANGUAGES = [
    {"key": "portugues", "label": "Português"},
    {"key": "ingles", "label": "Inglês"},
    {"key": "espanhol", "label": "Espanhol"},
    {"key": "frances", "label": "Francês"},
    {"key": "alemao", "label": "Alemão"},
    {"key": "italiano", "label": "Italiano"},
    {"key": "mandarim", "label": "Mandarim"},
    {"key": "japones", "label": "Japonês"},
    {"key": "coreano", "label": "Coreano"},
    {"key": "arabico", "label": "Árabe"},
]

LANGUAGE_LEVELS = [
    {"key": "basico", "label": "Básico"},
    {"key": "intermediario", "label": "Intermediário"},
    {"key": "avancado", "label": "Avançado"},
    {"key": "fluente", "label": "Fluente"},
]

STUDY_AREAS = [
    {"key": "ciencia_computacao", "label": "Ciência da Computação"},
    {"key": "engenharia_software", "label": "Engenharia de Software"},
    {"key": "sistemas_informacao", "label": "Sistemas de Informação"},
    {"key": "engenharia_computacao", "label": "Engenharia da Computação"},
    {"key": "ads", "label": "Análise e Desenvolvimento de Sistemas"},
    {"key": "ciencia_dados", "label": "Ciência de Dados"},
    {"key": "engenharia_eletrica", "label": "Engenharia Elétrica"},
    {"key": "matematica_aplicada", "label": "Matemática / Matemática Aplicada"},
    {"key": "redes_computadores", "label": "Redes de Computadores"},
    {"key": "seguranca_informacao", "label": "Segurança da Informação"},
]

STUDY_AREA_OUTRO = "outro"

MONTH_OPTIONS = list(range(1, 13))
MONTH_LABELS = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


def skill_key_to_label(key: str) -> str:
    return SKILL_LABELS.get(key, key)


def label_to_skill_key(label: str) -> str:
    for item in SKILLS:
        if item["label"] == label:
            return item["key"]
    raise ValueError(f"Skill não reconhecida: {label}")


def catalog_keys(items: list[dict[str, str]]) -> list[str]:
    return [item["key"] for item in items]


def catalog_label(items: list[dict[str, str]], key: str | None) -> str:
    if key is None:
        return ""
    for item in items:
        if item["key"] == key:
            return item["label"]
    return key


def format_month(month: int) -> str:
    return MONTH_LABELS.get(month, str(month))
