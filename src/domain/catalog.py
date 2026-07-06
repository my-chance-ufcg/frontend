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
    {"key": "graduacao_concluida", "label": "Graduação Concluída"},
    {"key": "pos_graduacao_andamento", "label": "Pós-Graduação em Andamento"},
    {"key": "pos_graduacao_concluida", "label": "Pós-Graduação Concluída"},
    {"key": "tecnico", "label": "Ensino Técnico"},
]

REGIONS = [
    {"key": "norte", "label": "Região Norte"},
    {"key": "nordeste", "label": "Região Nordeste"},
    {"key": "centro_oeste", "label": "Região Centro-Oeste"},
    {"key": "sudeste", "label": "Região Sudeste"},
    {"key": "sul", "label": "Região Sul"},
]

ROLE_TITLES = [
    "Desenvolvedor Backend Júnior",
    "Desenvolvedor Backend Pleno",
    "Desenvolvedor Frontend Júnior",
    "Desenvolvedor Frontend Pleno",
    "Desenvolvedor Full Stack Júnior",
    "Desenvolvedor Full Stack Pleno",
    "Analista de Dados Júnior",
    "Analista de Dados Pleno",
    "Engenheiro de Dados Júnior",
    "Engenheiro de Dados Pleno",
    "Estagiário de Desenvolvimento",
    "Estagiário de Dados",
]

INVITE_STATUS_LABELS = {
    "ENVIADO": "Aguardando sua resposta",
    "ACEITO": "Aceito — dados autorizados",
    "RECUSADO": "Recusado",
    "INVALIDADO": "Invalidado",
    "SUGERIDO": "Sugerido",
}


def label_to_skill_key(label: str) -> str:
    for item in SKILLS:
        if item["label"] == label:
            return item["key"]
    raise ValueError(f"Skill não reconhecida: {label}")
