import streamlit as st

st.title("Cadastro de Perfil Profissional")

# Banner de Anonimato
st.warning("⚠️ **Atenção:** Seu perfil é estritamente anônimo, qualquer informação sensível será ocultada, seu perfil será avaliado exclusivamente por suas competências técnicas.")

st.write("---")

# Competências Técnicas
st.subheader("1. Competências Técnicas")

if 'opcoes_skills' not in st.session_state:
    st.session_state.opcoes_skills = ["Python", "JavaScript", "React", "Node.js", "SQL", "PostgreSQL", "Docker", "AWS", "Machine Learning", "Streamlit"]

skills_selecionadas = st.multiselect(
    "Selecione suas principais Hard Skills:", 
    options=st.session_state.opcoes_skills,
    help="Essas habilidades serão usadas pelo nosso algoritmo para encontrar as vagas ideais para você."
)

# Adicionar skill customizada
col_nova_skill, col_btn_skill = st.columns([0.8, 0.2])
with col_nova_skill:
    nova_skill = st.text_input("Não encontrou uma competência específica? Digite e adicione:", key="input_nova_skill", placeholder="Ex: TypeScript, Go, Figma...")
with col_btn_skill:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("➕ Adicionar", use_container_width=True):
        if nova_skill:
            # Verifica se a skill já não existe na lista
            skills_lower = [s.lower() for s in st.session_state.opcoes_skills]
            if nova_skill.lower() not in skills_lower:
                st.session_state.opcoes_skills.append(nova_skill)
                st.rerun()
            else:
                st.warning("Essa competência já está na lista.")

st.write("---")

# Pretensão Salarial
st.subheader("2. Pretensão Salarial")
pretensao_minima = st.number_input(
    "Qual o valor mínimo mensal que você está disposto a aceitar em reais (R$)?",
    min_value=0,
    step=100,
    value=0,
    help="Vagas com orçamento inferior a este valor não serão recomendadas para você."
)

st.write("---")

# Histórico de Experiências
st.subheader("3. Histórico de Experiências")

if 'exp_ids' not in st.session_state:
    st.session_state.exp_ids = [0]
    st.session_state.next_id = 1

for exp_id in list(st.session_state.exp_ids):
    with st.container(border=True):
        col_conteudo, col_botao = st.columns([0.96, 0.04])
        
        with col_botao:
            if st.button("✖", key=f"del_{exp_id}", help="Remover esta experiência", type="tertiary"):
                st.session_state.exp_ids.remove(exp_id)
                st.rerun()
                
        st.text_input("Cargo (ex: Desenvolvedor Front-end Júnior)", key=f"cargo_{exp_id}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Tempo na função (em meses)", min_value=0, step=1, key=f"tempo_{exp_id}")
            
        st.text_area("Principais atividades e conquistas técnicas", key=f"ativ_{exp_id}", height=100)

if st.button("➕ Adicionar outra experiência"):
    st.session_state.exp_ids.append(st.session_state.next_id)
    st.session_state.next_id += 1
    st.rerun()

st.write("---")

# Projetos de Destaque
st.subheader("4. Projeto de Destaque")
projeto_destaque = st.text_area(
    "Descreva seu projeto mais significativo:", 
    placeholder="Inclua as tecnologias utilizadas, a arquitetura do projeto, os desafios superados e o impacto gerado...",
    height=150
)

st.write("---")

# Submissão
if st.button("Finalizar e Publicar Perfil Anônimo", type="primary", use_container_width=True):
    if len(skills_selecionadas) > 0 and pretensao_minima > 0:
        st.success(f"✅ Seu perfil anônimo foi salvo com sucesso!")
    else:
        st.error("Por favor, preencha pelo menos suas Hard Skills e insira uma pretensão salarial válida.")
