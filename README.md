# My Chance — Frontend

Interface web em Streamlit para candidatos e recrutadores. Consome a API REST do **backend-services**.

## Requisitos

- Python 3.12+
- Backend em execução (padrão: `http://localhost:8080`)

## Execução local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export MYCHANCE_API_BASE_URL=http://localhost:8080
streamlit run app.py
```

A aplicação abre em `http://localhost:8501`.

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `MYCHANCE_API_BASE_URL` | URL base da API do backend | `http://localhost:8080` |

## Estrutura

```
src/
├── config.py
├── domain/
├── services/
└── views/
```

## Contratos da API

Os payloads e respostas seguem o backend. Documentação canônica: `docs/api-contracts.md` no repositório **backend-services**.

## Docker

```bash
docker build -t mychance-frontend .
docker run --rm -p 8501:8501 \
  -e MYCHANCE_API_BASE_URL=http://host.docker.internal:8080 \
  mychance-frontend
```
