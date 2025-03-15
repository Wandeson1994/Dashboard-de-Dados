import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
import numpy as np

def process_csv_file(file, df=None):
    """
    Processa um arquivo CSV para extração de dados.
    Retorna o DataFrame e um dicionário de metadados.
    """
    if df is None:
        try:
            df = pd.read_csv(file)
        except Exception as e:
            st.error(f"Erro ao ler o arquivo CSV: {str(e)}")
            return None, None
    
    # Metadados básicos
    metadata = {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "dtypes": {col: str(df[col].dtype) for col in df.columns},
        "missing_values": df.isnull().sum().to_dict(),
        "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Adicionar estatísticas descritivas para colunas numéricas
    numeric_stats = {}
    for col in df.select_dtypes(include=['int64', 'float64']).columns:
        numeric_stats[col] = {
            "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
            "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
            "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
            "median": float(df[col].median()) if not pd.isna(df[col].median()) else None,
            "std": float(df[col].std()) if not pd.isna(df[col].std()) else None
        }
    
    metadata["numeric_stats"] = numeric_stats
    
    return df, metadata

def clean_dataframe(df):
    """Realiza limpeza básica no DataFrame."""
    # Criar uma cópia para não alterar o original
    cleaned_df = df.copy()
    
    # 1. Lidar com valores ausentes
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Valores Ausentes")
        missing_values = df.isnull().sum()
        cols_with_missing = missing_values[missing_values > 0]
        
        if len(cols_with_missing) > 0:
            st.write("Colunas com valores ausentes:")
            st.write(cols_with_missing)
            
            missing_strategy = st.selectbox(
                "Como tratar valores ausentes?",
                ["Manter", "Remover linhas", "Preencher com média/moda", "Preencher com zero"]
            )
            
            if missing_strategy == "Remover linhas":
                cleaned_df = cleaned_df.dropna()
                st.info(f"Removidas {len(df) - len(cleaned_df)} linhas com valores ausentes.")
            
            elif missing_strategy == "Preencher com média/moda":
                for col in cols_with_missing.index:
                    if df[col].dtype in ['int64', 'float64']:
                        # Para colunas numéricas, usamos a média
                        cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mean())
                    else:
                        # Para colunas categóricas, usamos a moda
                        cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mode()[0])
                st.info("Valores ausentes preenchidos com média/moda.")
            
            elif missing_strategy == "Preencher com zero":
                cleaned_df = cleaned_df.fillna(0)
                st.info("Valores ausentes preenchidos com zero.")
        else:
            st.info("Não há valores ausentes no conjunto de dados.")
    
    # 2. Detecção e tratamento de outliers para colunas numéricas
    with col2:
        st.subheader("Outliers")
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        if numeric_cols:
            outlier_col = st.selectbox("Verificar outliers em", numeric_cols)
            
            # Método de detecção de outliers usando IQR
            Q1 = cleaned_df[outlier_col].quantile(0.25)
            Q3 = cleaned_df[outlier_col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = cleaned_df[(cleaned_df[outlier_col] < lower_bound) | 
                            (cleaned_df[outlier_col] > upper_bound)]
            
            st.write(f"Número de outliers detectados: {len(outliers)}")
            
            if len(outliers) > 0:
                outlier_strategy = st.selectbox(
                    "Como tratar outliers?",
                    ["Manter", "Remover", "Limitar aos limites (capping)"]
                )
                
                if outlier_strategy == "Remover":
                    cleaned_df = cleaned_df[(cleaned_df[outlier_col] >= lower_bound) & 
                                        (cleaned_df[outlier_col] <= upper_bound)]
                    st.info(f"Removidos {len(outliers)} outliers.")
                
                elif outlier_strategy == "Limitar aos limites (capping)":
                    cleaned_df[outlier_col] = np.where(
                        cleaned_df[outlier_col] < lower_bound,
                        lower_bound,
                        np.where(
                            cleaned_df[outlier_col] > upper_bound,
                            upper_bound,
                            cleaned_df[outlier_col]
                        )
                    )
                    st.info(f"Outliers limitados aos limites ({lower_bound:.2f}, {upper_bound:.2f}).")
        else:
            st.info("Não há colunas numéricas para análise de outliers.")
    
    # 3. Opções para converter tipos de dados
    st.subheader("Converter Tipos de Dados")
    
    col1, col2 = st.columns(2)
    with col1:
        convert_col = st.selectbox("Selecione a coluna para converter", df.columns)
    
    with col2:
        target_type = st.selectbox(
            "Converter para",
            ["Manter tipo atual", "Numérico", "Texto", "Categoria", "Data/Hora"]
        )
    
    if target_type != "Manter tipo atual":
        try:
            if target_type == "Numérico":
                cleaned_df[convert_col] = pd.to_numeric(cleaned_df[convert_col], errors='coerce')
            elif target_type == "Texto":
                cleaned_df[convert_col] = cleaned_df[convert_col].astype(str)
            elif target_type == "Categoria":
                cleaned_df[convert_col] = cleaned_df[convert_col].astype('category')
            elif target_type == "Data/Hora":
                cleaned_df[convert_col] = pd.to_datetime(cleaned_df[convert_col], errors='coerce')
            
            st.success(f"Coluna {convert_col} convertida para {target_type}.")
        except Exception as e:
            st.error(f"Erro ao converter coluna: {str(e)}")
    
    # Exibir prévia dos dados limpos
    st.subheader("Prévia dos Dados Processados")
    st.dataframe(cleaned_df.head())
    
    return cleaned_df

def prepare_data_for_visualization(df, columns=None, sample_size=None, aggregation=None):
    """
    Prepara os dados para visualização em gráficos.
    
    Args:
        df: DataFrame a ser preparado
        columns: Lista de colunas a manter (opcional)
        sample_size: Tamanho da amostra (opcional)
        aggregation: Dicionário com configurações de agregação (opcional)
    
    Returns:
        DataFrame preparado para visualização
    """
    # Trabalhar com uma cópia
    result_df = df.copy()
    
    # Selecionar apenas as colunas especificadas
    if columns and all(col in df.columns for col in columns):
        result_df = result_df[columns]
    
    # Aplicar agregações se especificado
    if aggregation and isinstance(aggregation, dict):
        if all(k in result_df.columns for k in aggregation.keys()):
            group_by = aggregation.get('group_by')
            agg_column = aggregation.get('column')
            agg_func = aggregation.get('function', 'sum')
            
            if group_by and agg_column and group_by in result_df.columns and agg_column in result_df.columns:
                # Criar agregação
                if agg_func == 'sum':
                    result_df = result_df.groupby(group_by)[agg_column].sum().reset_index()
                elif agg_func == 'mean':
                    result_df = result_df.groupby(group_by)[agg_column].mean().reset_index()
                elif agg_func == 'count':
                    result_df = result_df.groupby(group_by)[agg_column].count().reset_index()
                elif agg_func == 'min':
                    result_df = result_df.groupby(group_by)[agg_column].min().reset_index()
                elif agg_func == 'max':
                    result_df = result_df.groupby(group_by)[agg_column].max().reset_index()
    
    # Reduzir o tamanho do dataset se necessário
    if sample_size and isinstance(sample_size, int) and sample_size < len(result_df):
        result_df = result_df.sample(sample_size, random_state=42)
    
    return result_df

def detect_date_columns(df):
    """
    Detecta e converte colunas que parecem ser datas.
    
    Args:
        df: DataFrame a ser analisado
    
    Returns:
        DataFrame com colunas de data convertidas
    """
    result_df = df.copy()
    date_columns = []
    
    # Verifica colunas que podem ser datas
    for col in result_df.columns:
        if result_df[col].dtype == 'object':
            # Tenta converter usando pandas
            try:
                # Amostragem para teste (mais rápido)
                sample = result_df[col].dropna().sample(min(100, len(result_df[col].dropna()))).copy()
                pd.to_datetime(sample, errors='raise', infer_datetime_format=True)
                
                # Se chegar aqui, a conversão funcionou na amostra
                result_df[col] = pd.to_datetime(result_df[col], errors='coerce')
                date_columns.append(col)
            except:
                continue
    
    return result_df, date_columns

def save_processed_file(df, original_filename):
    """Salva um dataframe processado no disco."""
    # Criar diretório se não existir
    save_dir = "data"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Gerar nome de arquivo único
    filename_parts = os.path.splitext(original_filename)
    base_name = filename_parts[0]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = os.path.join(save_dir, f"{base_name}_processed_{timestamp}.csv")
    
    # Salvar arquivo
    df.to_csv(file_path, index=False)
    
    return file_path 