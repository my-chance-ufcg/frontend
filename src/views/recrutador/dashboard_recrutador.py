import streamlit as st

st.title("Painel do Recrutador")

# Resumo da Conta
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Vagas Ativas", value="1")
with col2:
    st.metric(label="Convites Enviados", value="3")
with col3:
    st.metric(label="Entrevistas Confirmadas", value="1", delta="Nova!", delta_color="normal")

st.write("---")

# Gestão d candidatos
aba_confirmadas, aba_pendentes, aba_vagas = st.tabs(["Entrevistas Confirmadas", "Aguardando Resposta", "Minhas Vagas Ativas"])

# Entrevistas agendadas
with aba_confirmadas:
    st.subheader("Processos com Entrevista Firmada")
    st.markdown("Estes candidatos aceitaram o seu convite de entrevista. O compromisso da reunião foi selado e os dados de contato foram revelados.")
    
    # Mock candidato
    with st.container(border=True):
        col_info, col_acao = st.columns([0.55, 0.30])
          
        with col_info:
            st.markdown("#### Fulaninho Algumacoisa *(Anônimo #1042)*")
            st.markdown("**Vaga:** Desenvolvedor Back-end Pleno | **Match Técnico:** `95%`")
            st.markdown("fulaninho@exemplo.com.br &nbsp; | &nbsp; (99) 99999-9999")
            
        with col_acao:
            st.success("Reunião Confirmada")
            if st.button("Baixar CV Completo", key="cv_fulaninho", use_container_width=True):
                st.success("Download iniciado!")

# Parte dos convites ainda não aceitos
with aba_pendentes:
    st.subheader("Convites Pendentes")
    st.markdown("Você enviou propostas para estes candidatos, mas eles ainda não avaliaram o convite. A identidade permanece protegida.")
    
    # Mock candidato
    with st.container(border=True):
        col_info_anon, col_acao_anon = st.columns([0.55, 0.30])
        
        with col_info_anon:
            st.markdown("#### Candidato Anônimo #2105")
            st.markdown("**Vaga:** Desenvolvedor Back-end Pleno | **Match Técnico:** `82%`")
            st.markdown("*Dados de contato ocultos até o aceite da entrevista.*")
            
        with col_acao_anon:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            st.info("Aguardando candidato...")
            if st.button("Cancelar Convite", key="cancelar_2105", use_container_width=True):
                st.toast("Convite cancelado.")

# Gestão das vagas
with aba_vagas:
    st.subheader("Vagas em Andamento")
    
    with st.container(border=True):
        col_vaga, col_status = st.columns([0.7, 0.3])
        
        with col_vaga:
            st.markdown("### Desenvolvedor Back-end Pleno")
            st.markdown("**Orçamento Máximo:** R$ 7.000,00")
            st.markdown("**Requisitos:** Python, SQL, PostgreSQL, Docker, AWS")
            
        with col_status:
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            st.info("Buscando candidatos...")
            if st.button("Encerrar Vaga", key="encerrar_vaga_1", use_container_width=True):
                st.warning("Vaga encerrada.")
