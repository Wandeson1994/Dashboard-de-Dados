import streamlit as st
import pandas as pd
import os
from components.auth import login_required
from components.dashboard import dashboard_options
from components.file_processor import clean_dataframe

@login_required
def dashboard_page():
    st.title("📊 Dashboards Interativos")
    
    # Verificar se há arquivos processados
    if 'processed_files' not in st.session_state or not st.session_state.processed_files:
        st.warning("Nenhum arquivo processado disponível. Por favor, faça upload e processe arquivos na página de Upload.")
        st.info("Acesse a página 'Upload de Arquivos' para enviar arquivos CSV.")
        return
    
    # Lista de arquivos disponíveis
    file_options = list(st.session_state.processed_files.keys())
    
    # Layout com duas colunas para organizar a interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_file = st.selectbox("Selecione um arquivo para visualização", file_options)
    
    with col2:
        # Adicionar botão para limpar o dashboard atual
        if st.button("🗑️ Limpar Dashboard"):
            # Limpar a lista de gráficos existentes
            if 'charts' in st.session_state:
                st.session_state.charts = []
                st.success("Dashboard limpo com sucesso!")
                st.rerun()
    
    if selected_file:
        # Obter informações do arquivo
        file_info = st.session_state.processed_files[selected_file]
        file_path = file_info['path']
        
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            st.error(f"Arquivo não encontrado: {file_path}")
            return
        
        # Carregar o dataframe
        try:
            df = pd.read_csv(file_path)
            
            # Metadados
            with st.expander("Informações do arquivo"):
                metadata = file_info['metadata']
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Nome:** {selected_file}")
                    st.write(f"**Linhas:** {metadata['rows']}")
                
                with col2:
                    st.write(f"**Colunas:** {metadata['columns']}")
                    st.write(f"**Processado em:** {metadata.get('processed_at', 'N/A')}")
                
                with col3:
                    missing_values = sum(metadata['missing_values'].values())
                    st.write(f"**Valores ausentes:** {missing_values}")
                
                # Mostrar estatísticas numéricas se disponíveis
                if 'numeric_stats' in metadata and metadata['numeric_stats']:
                    st.subheader("Estatísticas Numéricas")
                    stats_df = pd.DataFrame()
                    
                    for col, stats in metadata['numeric_stats'].items():
                        stats_df[col] = pd.Series(stats)
                    
                    st.dataframe(stats_df.T)
            
            # Opções de limpeza de dados
            with st.expander("Pré-processamento de Dados", expanded=False):
                st.write("Utilize as opções abaixo para limpar e preparar seus dados para visualização.")
                clean_button = st.button("Limpar Dados")
                
                if clean_button:
                    df = clean_dataframe(df)
                    st.success("Dados limpos com sucesso!")
            
            # Mostrar instruções para o usuário
            st.info("Você pode adicionar múltiplos gráficos nesta página. Clique em '➕ Adicionar Novo Gráfico' para começar.")
            
            # Opções de dashboard - agora com suporte a múltiplos gráficos
            dashboard_options(df)
            
            # Exibir dados
            with st.expander("Ver dados completos", expanded=False):
                st.dataframe(df)
            
        except Exception as e:
            st.error(f"Erro ao carregar o arquivo: {str(e)}")
    else:
        st.info("Selecione um arquivo da lista para criar dashboards.")

if __name__ == "__main__":
    dashboard_page() 