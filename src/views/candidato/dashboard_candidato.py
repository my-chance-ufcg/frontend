import streamlit as st

st.title("Painel do Candidato")

# Resumo do Perfil
st.metric(label="Status do Perfil", value="Ativo / Anônimo", help="Seu perfil está visível para recrutadores de forma anonimizada.")
st.write("---")

# Gestão de Convites
st.subheader("Convites para Entrevista")
st.markdown("Recrutadores demonstraram interesse no seu perfil. Avalie as propostas abaixo:")

# Mock de Convites Recebidos
if 'convites' not in st.session_state:
    st.session_state.convites = [
        {
            "id": 1,
            "empresa_id": "Empresa A", 
            "cargo": "Desenvolvedor Python Júnior",
            "salario_oferecido": 5500.00,
            "descricao_vaga": "Atuação em projetos de análise de dados e automação de processos industriais.",
            "requisitos": "Python, SQL, Docker",
            "status": "pendente"
        },
        {
            "id": 2,
            "empresa_id": "Empresa B",
            "cargo": "Desenvolvedor Front-end Pleno",
            "salario_oferecido": 7200.00,
            "descricao_vaga": "Desenvolvimento de interfaces modernas para plataforma de E-commerce internacional.",
            "requisitos": "React, TypeScript, Tailwind CSS",
            "status": "pendente"
        }
    ]

# Cards de Convite
convites_pendentes = [c for c in st.session_state.convites if c["status"] == "pendente"]

if len(convites_pendentes) > 0:
    for convite in convites_pendentes:
        with st.container(border=True):
            st.markdown(f"### Proposta para: **{convite['cargo']}**")
            st.markdown(f"**Salário Oferecido:** R$ {convite['salario_oferecido']:,.2f}")
            
            with st.expander("Ver detalhes da oportunidade"):
                st.write(f"**Sobre a vaga:** {convite['descricao_vaga']}")
                st.write(f"**Requisitos esperados:** {convite['requisitos']}")
                st.info("Ao autorizar, seu nome, e-mail e currículo completo serão revelados para esta empresa.")

            col_aut, col_rec = st.columns(2)
            with col_aut:
                if st.button("Autorizar Revelação de Dados", key=f"aut_{convite['id']}", use_container_width=True, type="primary"):
                    convite["status"] = "autorizado"
                    st.toast("Identidade revelada! Boa sorte na sua entrevista!")
                    st.rerun()
            with col_rec:
                if st.button("Recusar Proposta", key=f"rec_{convite['id']}", use_container_width=True):
                    convite["status"] = "recusado"
                    st.toast("Proposta removida da sua lista.")
                    st.rerun()
else:
    st.info("Você ainda não possui novos convites. Continue aprimorando seu currículo para atrair mais recrutadores!")
