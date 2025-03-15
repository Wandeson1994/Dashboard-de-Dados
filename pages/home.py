import streamlit as st
from components.auth import login_required

@login_required
def home_page():
    st.title("📊 Dashboard Interativo")
    
    # Informações sobre o usuário
    st.write(f"Bem-vindo, {st.session_state.user_info['name']}!")
    
    # Layout em colunas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sobre a Aplicação")
        st.write("""
        Esta aplicação permite carregar arquivos CSV, processá-los e criar dashboards 
        interativos para visualização e análise de dados.
        
        Os recursos incluem:
        - Upload de múltiplos arquivos
        - Pré-processamento de dados
        - Criação de gráficos personalizados
        - Filtros dinâmicos
        """)
        
    with col2:
        st.subheader("Primeiros Passos")
        st.markdown("""
        1. 📁 Acesse **Upload de Arquivos** para enviar seus dados
        2. 🔍 Use a página **Processar Dados** para limpar e preparar seus dados
        3. 📊 Crie visualizações na página **Dashboards**
        """)
    
    # Estatísticas (para demonstração)
    st.subheader("Estatísticas da Sessão")
    stats_cols = st.columns(3)
    with stats_cols[0]:
        st.metric(label="Arquivos Processados", value="0")
    with stats_cols[1]:
        st.metric(label="Dashboards Criados", value="0")
    with stats_cols[2]:
        st.metric(label="Tempo de Sessão", value="0 min")
    
    # Card com dica
    st.info("""
    💡 **Dica**: Para melhores resultados, certifique-se de que seus dados estão bem estruturados, 
    com nomes de colunas adequados e sem valores ausentes.
    """)

if __name__ == "__main__":
    home_page() 