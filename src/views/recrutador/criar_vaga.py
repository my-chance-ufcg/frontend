import streamlit as st

st.title("Cadastro de Nova Vaga")
st.markdown("Preencha os dados da vaga.")

st.write("---")

# Informações Básicas
st.subheader("1. Informações Básicas")
titulo_vaga = st.text_input("Título da Vaga (ex: Desenvolvedor Back-end Pleno)")
descricao_vaga = st.text_area(
    "Descrição Técnica", 
    height=120, 
    placeholder="Descreva as responsabilidades, o ambiente de trabalho e os desafios da posição..."
)

st.write("---")

# Remuneração máxima aceitável
st.subheader("2. Orçamento Salarial")
salario_maximo = st.number_input(
    "Qual o valor máximo mensal que a empresa está disposta a pagar em reais (R$)?",
    min_value=0,
    step=100,
    value=0,
    help="Candidatos com pretensão salarial mínima maior do que este valor serão desconsiderados no matching."
)

st.write("---")

# Requisitos Técnicos
st.subheader("3. Requisitos Técnicos (Hard Skills)")
opcoes_skills = ["Python", "JavaScript", "React", "Node.js", "Express", "Sequelize", "SQL", "PostgreSQL", "Docker", "AWS", "Machine Learning", "Streamlit"]

skills_obrigatorias = st.multiselect(
    "Competências Obrigatórias:", 
    opcoes_skills,
    help="Candidatos que não possuírem estas habilidades serão filtrados automaticamente."
)

skills_desejaveis = st.multiselect(
    "Competências Desejáveis (Diferenciais):", 
    opcoes_skills,
    help="Habilidades que aumentam a pontuação de compatibilidade do candidato."
)

st.write("---")

# Criar vaga
if st.button("Criar Vaga e Buscar Candidatos", type="primary", use_container_width=True):
    if titulo_vaga and len(skills_obrigatorias) > 0 and salario_maximo > 0:
        st.success(f"Vaga cadastrada com sucesso com teto orçamentário de R$ {salario_maximo:,.2f}!")
    else:
        st.error("Por favor, preencha o Título, as Competências Obrigatórias e insira um valor de orçamento válido.")

