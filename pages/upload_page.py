import streamlit as st
import os
import pandas as pd
from components.auth import login_required
from components.file_processor import process_csv_file, save_processed_file

@login_required
def upload_page():
    st.title("📁 Upload de Arquivos")
    
    # Configurações do upload
    st.write("Selecione os arquivos que deseja enviar para análise.")
    
    uploaded_files = st.file_uploader(
        "Arraste e solte os arquivos ou clique para selecionar",
        type=['csv', 'txt', 'png', 'jpg'],
        accept_multiple_files=True,
        help="Selecione os arquivo(s) que deseja enviar para processamento"
    )
    
    # Inicializar sessão para arquivos processados
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = {}
    
    # Exibir informações sobre os arquivos enviados
    if uploaded_files:
        st.subheader("Arquivos Enviados:")
        
        # Loop através dos arquivos enviados
        for file in uploaded_files:
            expander = st.expander(f"{file.name} ({round(file.size / 1024, 2)} KB)")
            
            with expander:
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Exibir nome do arquivo
                    st.write(f"**Nome do Arquivo:** {file.name}")
                    
                    # Formatar tamanho do arquivo
                    size = round(file.size / 1000000, 2)
                    st.write(f"**Tamanho:** {size} MB")
                    
                    # Exibir tipo do arquivo
                    st.write(f"**Tipo do Arquivo:** {file.type}")
                
                with col2:
                    # Tentar exibir conteúdo do arquivo (dependendo do tipo)
                    try:
                        if file.type.startswith('image'):
                            # Se for imagem, exiba-a
                            st.image(file.read(), use_column_width=True)
                            file.seek(0)  # Resetar o ponteiro do arquivo
                        elif file.type == 'text/csv':
                            # Se for CSV, leia e exiba os dados
                            data = pd.read_csv(file)
                            st.write(data.head())
                            file.seek(0)  # Resetar o ponteiro do arquivo
                            
                            # Processar o arquivo para extrair informações
                            df, metadata = process_csv_file(file, df=data)
                            
                            if df is not None and metadata is not None:
                                # Exibir estatísticas básicas
                                st.write(f"**Linhas:** {metadata['rows']}, **Colunas:** {metadata['columns']}")
                                
                                # Botão para processar dados
                                if st.button(f"Processar {file.name}", key=f"process_{file.name}"):
                                    # Salvar o arquivo
                                    save_dir = "data"
                                    if not os.path.exists(save_dir):
                                        os.makedirs(save_dir)
                                    
                                    file_path = save_processed_file(df, file.name)
                                    
                                    # Armazenar metadados na sessão
                                    st.session_state.processed_files[file.name] = {
                                        'path': file_path,
                                        'metadata': metadata,
                                        'processed': True
                                    }
                                    
                                    st.success(f"Arquivo {file.name} processado e salvo! Acesse a página de Dashboards para visualizá-lo.")
                        else:
                            # Para outros tipos de arquivo, mostre informações básicas
                            st.info("O conteúdo completo deste tipo de arquivo não pode ser visualizado aqui.")
                    except Exception as e:
                        st.error(f"Erro ao ler o arquivo: {str(e)}")
        
        # Pasta onde os arquivos serão salvos
        save_dir = "arquivos_enviados"
        
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Botão para salvar todos os arquivos
        if st.button("Salvar Todos os Arquivos"):
            # Salvar cada arquivo na pasta especificada
            for file in uploaded_files:
                with open(os.path.join(save_dir, file.name), "wb") as f:
                    f.write(file.getbuffer())
            
            st.success(f"Todos os arquivos foram salvos com sucesso em: {save_dir}")
    else:
        st.info("Nenhum arquivo selecionado. Arraste e solte os arquivos ou clique no seletor acima.")
    
    # Exibir arquivos processados
    if st.session_state.processed_files:
        st.subheader("Arquivos Processados")
        
        # Criar tabela com os arquivos processados
        data = []
        for filename, info in st.session_state.processed_files.items():
            data.append({
                "Nome do Arquivo": filename,
                "Linhas": info['metadata']['rows'],
                "Colunas": info['metadata']['columns'],
                "Caminho": info['path']
            })
        
        if data:
            df_processed = pd.DataFrame(data)
            st.dataframe(df_processed)

if __name__ == "__main__":
    upload_page() 