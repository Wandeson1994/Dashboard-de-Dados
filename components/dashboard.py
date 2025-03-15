import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import uuid
import datetime
from components.file_processor import prepare_data_for_visualization, detect_date_columns

def get_data_preview(df, num_rows=5):
    """Retorna uma prévia dos dados."""
    return df.head(num_rows)

def save_dataframe(df, file_name):
    """Salva o dataframe na pasta data."""
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    file_path = os.path.join(data_dir, file_name)
    df.to_csv(file_path, index=False)
    return file_path

def get_column_types(df):
    """Classifica as colunas do dataframe por tipo."""
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    return {
        'numeric': numeric_cols,
        'categorical': categorical_cols,
        'date': date_cols
    }

def create_chart(df, chart_type, x_col, y_col, color_col=None, title="Dashboard Interativo", theme="plotly", height=500):
    """Cria diferentes tipos de gráficos com base nos parâmetros."""
    try:
        # Verificar dados de entrada
        if df.empty:
            st.warning("DataFrame vazio. Não é possível criar o gráfico.")
            return None
            
        if x_col not in df.columns:
            st.error(f"Coluna do eixo X não encontrada: {x_col}")
            return None
            
        if y_col is not None and y_col not in df.columns and chart_type != "Histograma":
            st.error(f"Coluna do eixo Y não encontrada: {y_col}")
            return None
            
        if color_col is not None and color_col not in df.columns:
            st.warning(f"Coluna de cor não encontrada: {color_col}. Usando sem colorização.")
            color_col = None
            
        # Configurar o tema
        template = theme if theme in ["plotly", "plotly_white", "ggplot2", "seaborn", "simple_white"] else "plotly"
        
        # Tratar valores ausentes nas colunas selecionadas
        chart_df = df.copy()
        
        # Remover valores nulos das colunas usadas no gráfico para evitar erros
        cols_to_check = [x_col]
        if y_col is not None:
            cols_to_check.append(y_col)
        if color_col is not None:
            cols_to_check.append(color_col)
            
        chart_df = chart_df.dropna(subset=cols_to_check)
        
        if chart_df.empty:
            st.warning("Após remover valores ausentes, não há dados para exibir.")
            return None
        
        # Criar o gráfico de acordo com o tipo selecionado
        if chart_type == "Barra":
            fig = px.bar(chart_df, x=x_col, y=y_col, color=color_col, title=title, template=template)
        
        elif chart_type == "Linha":
            fig = px.line(chart_df, x=x_col, y=y_col, color=color_col, title=title, template=template)
        
        elif chart_type == "Dispersão":
            fig = px.scatter(chart_df, x=x_col, y=y_col, color=color_col, title=title, template=template)
        
        elif chart_type == "Histograma":
            fig = px.histogram(chart_df, x=x_col, title=title, template=template)
        
        elif chart_type == "Pizza":
            # Correção para gráfico de pizza
            try:
                # Contar valores e preparar dados para pizza
                if chart_df[x_col].nunique() > 10:
                    st.warning(f"A coluna {x_col} tem muitos valores únicos ({chart_df[x_col].nunique()}). O gráfico de pizza pode ficar confuso.")
                
                # Agrupar dados se y_col for fornecido, caso contrário usar contagem
                if y_col is not None and y_col in chart_df.columns:
                    # Somar valores de y agrupados por x
                    grouped = chart_df.groupby(x_col)[y_col].sum().reset_index()
                    fig = px.pie(grouped, values=y_col, names=x_col, title=title, template=template)
                else:
                    # Contar ocorrências de cada valor em x_col
                    counts = chart_df[x_col].value_counts().reset_index()
                    counts.columns = [x_col, 'count']
                    fig = px.pie(counts, values='count', names=x_col, title=title, template=template)
            except Exception as e:
                st.error(f"Erro ao criar gráfico de pizza: {str(e)}")
                return None
        
        elif chart_type == "Heatmap":
            # Correção para heatmap
            try:
                if color_col is None:
                    st.error("Para criar um heatmap, selecione uma coluna para colorir.")
                    return None
                
                # Criar tabela pivot agrupando os dados
                if y_col is not None:
                    # Verificar se há dados suficientes para criar o pivot
                    if chart_df[x_col].nunique() * chart_df[color_col].nunique() > 1000:
                        st.warning("Dados muito grandes para heatmap. Limitando a amostra.")
                        chart_df = chart_df.sample(min(1000, len(chart_df)))
                        
                    pivot_table = pd.pivot_table(chart_df, values=y_col, index=x_col, columns=color_col, aggfunc='mean')
                    fig = px.imshow(pivot_table, 
                                   labels=dict(x=color_col, y=x_col, color=y_col),
                                   title=title,
                                   template=template)
                else:
                    st.error("Para criar um heatmap, selecione uma coluna para o eixo Y.")
                    return None
            except Exception as e:
                st.error(f"Erro ao criar heatmap: {str(e)}")
                return None
        
        else:
            st.error(f"Tipo de gráfico não suportado: {chart_type}")
            return None
        
        # Adicionar layout responsivo
        fig.update_layout(
            autosize=True,
            height=height,
            margin=dict(l=10, r=10, t=50, b=10),
        )
        
        return fig
    except Exception as e:
        st.error(f"Erro inesperado ao criar o gráfico: {str(e)}")
        return None

def configure_chart(df, chart_id):
    """Interface para configurar um gráfico individual."""
    try:
        # Verificar se o DataFrame está vazio
        if df.empty:
            st.warning("O conjunto de dados está vazio. Não é possível configurar o gráfico.")
            return None
        
        # Primeiro, oferecer opções de pré-processamento de dados
        st.write("🔍 **Pré-processamento para este gráfico**")
        
        # Detectar e converter colunas de data
        detect_dates = st.checkbox("Detectar e converter colunas de data", value=True, key=f"detect_dates_{chart_id}")
        
        # Amostrar dados para gráficos mais rápidos
        sample_data = st.checkbox("Amostrar dados (para datasets grandes)", key=f"sample_{chart_id}")
        sample_size = None
        if sample_data:
            sample_size = st.slider("Tamanho da amostra", 
                                  min_value=100, 
                                  max_value=min(10000, len(df)), 
                                  value=min(1000, len(df)), 
                                  step=100, 
                                  key=f"sample_size_{chart_id}")
        
        # Opção para agregação
        perform_agg = st.checkbox("Realizar agregação de dados", key=f"agg_{chart_id}")
        agg_config = None
        
        if perform_agg:
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if not numeric_cols:
                st.warning("Não há colunas numéricas disponíveis para agregação.")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    group_by_col = st.selectbox("Agrupar por", df.columns.tolist(), key=f"group_by_{chart_id}")
                with col2:
                    agg_col = st.selectbox("Coluna para agregação", numeric_cols, key=f"agg_col_{chart_id}")
                
                agg_func = st.selectbox("Função de agregação", ["sum", "mean", "count", "min", "max"], key=f"agg_func_{chart_id}")
                
                agg_config = {
                    'group_by': group_by_col,
                    'column': agg_col,
                    'function': agg_func
                }
        
        # Botão para aplicar pré-processamento
        apply_preprocessing = st.button("Aplicar Pré-processamento", key=f"apply_preprocess_{chart_id}")
        
        # Processar os dados conforme as opções selecionadas
        processed_df = df.copy()
        
        if apply_preprocessing:
            try:
                # Detectar e converter datas
                if detect_dates:
                    processed_df, date_cols = detect_date_columns(processed_df)
                    if date_cols:
                        st.success(f"Colunas de data detectadas e convertidas: {', '.join(date_cols)}")
                
                # Aplicar agregações se solicitado
                if perform_agg and agg_config:
                    processed_df = prepare_data_for_visualization(
                        processed_df, 
                        sample_size=sample_size,
                        aggregation=agg_config
                    )
                    st.success(f"Dados agregados: {agg_config['column']} por {agg_config['group_by']} usando {agg_config['function']}")
                # Aplicar amostragem se solicitado (sem agregação)
                elif sample_data and sample_size:
                    processed_df = prepare_data_for_visualization(
                        processed_df,
                        sample_size=sample_size
                    )
                    st.success(f"Amostra de {sample_size} linhas aplicada.")
            except Exception as e:
                st.error(f"Erro no pré-processamento: {str(e)}")
                # Voltar ao DataFrame original em caso de erro
                processed_df = df.copy()
        
        # Proteger contra DataFrame vazio após pré-processamento
        if processed_df.empty:
            st.warning("O pré-processamento resultou em um conjunto de dados vazio. Usando dados originais.")
            processed_df = df.copy()
        
        # Obter tipos de colunas para o DataFrame processado
        col_types = get_column_types(processed_df)
        
        # Interface para seleção de tipo de gráfico
        chart_types = ["Barra", "Linha", "Dispersão", "Histograma", "Pizza", "Heatmap"]
        
        # Obter a configuração atual do gráfico
        current_chart = next((c for c in st.session_state.charts if c['id'] == chart_id), None)
        default_type = 'Barra'
        if current_chart and 'config' in current_chart:
            default_type = current_chart['config'].get('type', 'Barra')
        
        chart_type = st.selectbox("Selecione o tipo de gráfico", 
                               chart_types, 
                               index=chart_types.index(default_type) if default_type in chart_types else 0,
                               key=f"chart_type_{chart_id}")
        
        # Selecionar colunas com base no tipo de gráfico
        col1, col2 = st.columns(2)
        
        with col1:
            # Opções para eixo X
            if chart_type == "Histograma":
                x_options = col_types['numeric']
                if not x_options:
                    st.warning("Não há colunas numéricas disponíveis para o eixo X.")
                    x_options = processed_df.columns.tolist()  # Fallback para todas as colunas
            else:
                x_options = processed_df.columns.tolist()
            
            if not x_options:
                st.warning("Não há colunas disponíveis para o eixo X.")
                return None
                
            x_col = st.selectbox("Selecione a coluna para o eixo X", x_options, key=f"x_col_{chart_id}")
        
        with col2:
            # Opções para eixo Y (não necessário para alguns gráficos)
            if chart_type not in ["Histograma"]:
                y_options = col_types['numeric'] if len(col_types['numeric']) > 0 else processed_df.columns.tolist()
                if not y_options:
                    st.warning("Não há colunas numéricas disponíveis para o eixo Y.")
                    return None
                    
                y_col = st.selectbox("Selecione a coluna para o eixo Y", y_options, key=f"y_col_{chart_id}")
            else:
                y_col = None
        
        # Opção para colorir por categoria
        if chart_type == "Heatmap":
            color_options = col_types['categorical'] if col_types['categorical'] else processed_df.columns.tolist()
            if not color_options:
                st.warning("Não há colunas categóricas disponíveis para colorir.")
                return None
                
            color_col = st.selectbox("Selecione a coluna para colunas do heatmap", color_options, key=f"color_col_{chart_id}")
        else:
            color_options = [None] + col_types['categorical']
            color_col = st.selectbox("Colorir por (opcional)", color_options, key=f"color_col_{chart_id}")
        
        # Opções de filtragem
        filters = {}
        st.write("🔍 **Filtros**")
        # Verificar se há colunas categóricas
        if col_types['categorical']:
            # Criar filtros para colunas categóricas
            for i, col in enumerate(col_types['categorical'][:3]):  # Limitar a 3 filtros para simplicidade
                try:
                    unique_values = processed_df[col].unique().tolist()
                    if len(unique_values) < 10:  # Apenas mostrar filtro se houver poucos valores únicos
                        selected = st.multiselect(f"Filtrar {col}", unique_values, default=unique_values, key=f"filter_{i}_{chart_id}")
                        if selected and len(selected) < len(unique_values):
                            filters[col] = selected
                except Exception as e:
                    st.error(f"Erro ao criar filtro para {col}: {str(e)}")
        else:
            st.info("Não há colunas categóricas disponíveis para filtrar.")
        
        # Aplicar filtros
        try:
            filtered_df = processed_df.copy()
            for col, values in filters.items():
                filtered_df = filtered_df[filtered_df[col].isin(values)]
            
            # Proteger contra DataFrame vazio após filtros
            if filtered_df.empty:
                st.warning("Os filtros aplicados resultam em um conjunto de dados vazio. Usando dados sem filtros.")
                filtered_df = processed_df.copy()
        except Exception as e:
            st.error(f"Erro ao aplicar filtros: {str(e)}")
            filtered_df = processed_df.copy()
        
        # Opções de aparência do gráfico
        st.write("🎨 **Aparência**")
        # Título do gráfico
        default_title = f"Gráfico {chart_id[:4]}"
        if current_chart and 'config' in current_chart:
            default_title = current_chart['config'].get('title', default_title)
            
        chart_title = st.text_input("Título do gráfico", default_title, key=f"title_{chart_id}")
        
        # Cor do tema
        color_themes = ["plotly", "plotly_white", "ggplot2", "seaborn", "simple_white"]
        default_theme = "plotly"
        if current_chart and 'config' in current_chart:
            default_theme = current_chart['config'].get('theme', default_theme)
            
        color_theme = st.selectbox(
            "Tema de cores", 
            color_themes,
            index=color_themes.index(default_theme) if default_theme in color_themes else 0,
            key=f"theme_{chart_id}"
        )
        
        # Altura do gráfico
        default_height = 500
        if current_chart and 'config' in current_chart:
            default_height = current_chart['config'].get('height', default_height)
            
        chart_height = st.slider("Altura do gráfico", 300, 800, default_height, 50, key=f"height_{chart_id}")
        
        # Configuração para criar o gráfico
        chart_config = {
            'type': chart_type,
            'x_col': x_col,
            'y_col': y_col,
            'color_col': color_col,
            'title': chart_title,
            'filters': filters,
            'theme': color_theme,
            'height': chart_height
        }
        
        # Atualizar a configuração no objeto de gráfico
        for chart in st.session_state.charts:
            if chart['id'] == chart_id:
                chart['config'] = chart_config
                break
        
        return {
            'config': chart_config,
            'df': filtered_df
        }
    except Exception as e:
        st.error(f"Erro ao configurar o gráfico: {str(e)}")
        return None

def export_dashboard_config():
    """Exporta a configuração atual do dashboard para JSON."""
    if 'charts' not in st.session_state or not st.session_state.charts:
        st.warning("Não há configurações de dashboard para exportar.")
        return
    
    # Criar diretório config se não existir
    config_dir = 'config'
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    # Preparar dados para exportação
    dashboard_config = {
        'charts': st.session_state.charts,
        'layout': st.session_state.get('layout_cols', 2),
        'created_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Gerar nome do arquivo
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"dashboard_config_{timestamp}.json"
    file_path = os.path.join(config_dir, filename)
    
    # Salvar arquivo
    with open(file_path, 'w') as f:
        json.dump(dashboard_config, f, indent=4)
    
    return file_path

def import_dashboard_config(config_file):
    """Importa configuração de dashboard a partir de um arquivo JSON."""
    try:
        # Ler arquivo de configuração
        with open(config_file.name, 'r') as f:
            config = json.load(f)
        
        # Verificar se a configuração é válida
        if 'charts' not in config:
            st.error("Arquivo de configuração inválido.")
            return False
        
        # Atualizar configurações na sessão
        st.session_state.charts = config['charts']
        
        if 'layout' in config:
            st.session_state.layout_cols = config['layout']
        
        return True
    except Exception as e:
        st.error(f"Erro ao importar configuração: {str(e)}")
        return False

def dashboard_options(df):
    """Interface para configurar e exibir múltiplos dashboards."""
    
    st.subheader("Dashboard Interativo")
    
    # Inicializar a lista de gráficos na sessão se não existir
    if 'charts' not in st.session_state:
        st.session_state.charts = []
    
    # Opções para adicionar novo gráfico ou gerenciar os existentes
    with st.expander("⚙️ Gerenciar Gráficos", expanded=True):
        # Layout com 3 colunas para os botões
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Botão para adicionar um novo gráfico
            add_chart = st.button("➕ Adicionar Novo Gráfico")
        
        with col2:
            # Botão para exportar configuração
            export_btn = st.button("💾 Exportar Dashboard")
        
        with col3:
            # Opção para importar configuração
            import_file = st.file_uploader("📂 Importar Dashboard", type="json", accept_multiple_files=False)
        
        if add_chart:
            try:
                # Gerar ID único para o novo gráfico
                chart_id = str(uuid.uuid4())
                
                # Adicionar gráfico com valores padrão
                # Isso garante que todos os campos necessários estejam presentes
                st.session_state.charts.append({
                    'id': chart_id,
                    'visible': True,
                    'order': len(st.session_state.charts),
                    'config': {
                        'type': 'Barra',  # Tipo padrão
                        'title': f"Novo Gráfico {len(st.session_state.charts)+1}",
                        'theme': 'plotly',
                        'height': 500
                    }
                })
                
                st.success("Novo gráfico adicionado! Configure-o abaixo.")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao adicionar novo gráfico: {str(e)}")
        
        if export_btn:
            file_path = export_dashboard_config()
            if file_path:
                st.success(f"Dashboard exportado com sucesso: {file_path}")
        
        if import_file:
            if import_dashboard_config(import_file):
                st.success("Dashboard importado com sucesso!")
                st.rerun()
        
        # Exibir lista de gráficos para gerenciamento
        if st.session_state.charts:
            st.subheader("Gráficos Configurados")
            
            # Opção para organizar o layout
            layout_col1, layout_col2 = st.columns(2)
            
            with layout_col1:
                # Opção para reorganizar gráficos
                col_layout = st.radio("Layout de colunas", [1, 2, 3], key="layout_cols", index=1)
            
            with layout_col2:
                # Opção para modo de visualização
                view_mode = st.radio("Modo de visualização", ["Normal", "Compacto"], key="view_mode", index=0)
            
            # Tabela para gerenciar gráficos
            st.write("### Organize seus gráficos")
            
            # Header da tabela
            col_header1, col_header2, col_header3, col_header4, col_header5 = st.columns([1, 3, 1, 1, 1])
            with col_header1:
                st.write("**Nº**")
            with col_header2:
                st.write("**Gráfico**")
            with col_header3:
                st.write("**Visível**")
            with col_header4:
                st.write("**Ordem**")
            with col_header5:
                st.write("**Remover**")
            
            # Opção para excluir ou ocultar gráficos
            charts_to_remove = []
            reorder_needed = False
            
            # Garantir que todos os gráficos tenham uma ordem definida
            for i, chart in enumerate(st.session_state.charts):
                if 'order' not in chart:
                    chart['order'] = i
            
            # Ordenar a lista de gráficos pela ordem definida
            sorted_charts = sorted(enumerate(st.session_state.charts), key=lambda x: x[1].get('order', x[0]))
            
            for i, (orig_idx, chart) in enumerate(sorted_charts):
                col1, col2, col3, col4, col5 = st.columns([1, 3, 1, 1, 1])
                
                with col1:
                    st.write(f"{i+1}")
                
                with col2:
                    st.write(f"ID: {chart['id'][:6]}...")
                
                with col3:
                    if st.checkbox("", value=chart['visible'], key=f"visible_{chart['id']}"):
                        chart['visible'] = True
                    else:
                        chart['visible'] = False
                
                with col4:
                    # Botões para mover para cima/baixo
                    if i > 0:
                        if st.button("↑", key=f"up_{chart['id']}"):
                            # Trocar ordem com o gráfico anterior
                            prev_chart = st.session_state.charts[sorted_charts[i-1][0]]
                            current_order = chart.get('order', i)
                            prev_order = prev_chart.get('order', i-1)
                            
                            chart['order'] = prev_order
                            prev_chart['order'] = current_order
                            reorder_needed = True
                
                with col5:
                    if st.button("🗑️", key=f"delete_{chart['id']}"):
                        charts_to_remove.append(orig_idx)
            
            # Remover gráficos marcados para exclusão
            for i in sorted(charts_to_remove, reverse=True):
                del st.session_state.charts[i]
                
            if charts_to_remove or reorder_needed:
                st.rerun()
    
    # Exibir gráficos configurados
    if st.session_state.charts:
        # Determinar o layout de colunas
        n_cols = st.session_state.get("layout_cols", 2)
        view_mode = st.session_state.get("view_mode", "Normal")
        compact_mode = view_mode == "Compacto"
        
        # Criar configuração de colunas
        visible_charts = [chart for chart in st.session_state.charts if chart['visible']]
        
        # Ordenar os gráficos visíveis pela ordem definida
        visible_charts = sorted(visible_charts, key=lambda x: x.get('order', 0))
        
        # Se não houver gráficos visíveis, exibir mensagem
        if not visible_charts:
            st.info("Nenhum gráfico visível. Adicione um novo gráfico ou torne um existente visível.")
            return
        
        # Adicionar opção para alternar entre visualização por tabs ou colunas
        if len(visible_charts) > 1 and not compact_mode:
            view_tabs = st.checkbox("Ver gráficos em abas", value=False, key="view_tabs")
        else:
            view_tabs = False
        
        if view_tabs:
            # Criar tabs para cada gráfico
            tabs = st.tabs([f"Gráfico #{i+1}" for i in range(len(visible_charts))])
            
            for i, (tab, chart) in enumerate(zip(tabs, visible_charts)):
                with tab:
                    st.markdown(f"### Configuração do Gráfico #{i+1}")
                    chart_data = configure_chart(df, chart['id'])
                    
                    # Se o gráfico foi configurado corretamente, exibi-lo
                    if chart_data:
                        config = chart_data['config']
                        filtered_df = chart_data['df']
                        
                        # Criar e exibir o gráfico
                        create_and_display_chart(config, filtered_df)
        else:
            # Criar layout de colunas para exibir gráficos
            if compact_mode:
                # No modo compacto, cada gráfico ocupa toda a largura
                for i, chart in enumerate(visible_charts):
                    st.markdown(f"### Gráfico #{i+1}")
                    st.markdown("#### Configuração")
                    chart_data = configure_chart(df, chart['id'])
                    
                    # Se o gráfico foi configurado corretamente, exibi-lo
                    if chart_data:
                        config = chart_data['config']
                        filtered_df = chart_data['df']
                        
                        st.markdown("#### Visualização")
                        # Criar e exibir o gráfico
                        create_and_display_chart(config, filtered_df)
                    
                    # Adicionar separador entre gráficos
                    if i < len(visible_charts) - 1:
                        st.markdown("---")
            else:
                # Layout em colunas
                for i in range(0, len(visible_charts), n_cols):
                    cols = st.columns(n_cols)
                    
                    for j in range(n_cols):
                        idx = i + j
                        if idx < len(visible_charts):
                            chart = visible_charts[idx]
                            with cols[j]:
                                st.markdown(f"### Gráfico #{idx+1}")
                                st.markdown("#### Configuração")
                                chart_data = configure_chart(df, chart['id'])
                                
                                # Se o gráfico foi configurado corretamente, exibi-lo
                                if chart_data:
                                    config = chart_data['config']
                                    filtered_df = chart_data['df']
                                    
                                    st.markdown("#### Visualização")
                                    # Criar e exibir o gráfico
                                    create_and_display_chart(config, filtered_df)
    else:
        st.info("Clique em 'Adicionar Novo Gráfico' para começar a criar seu dashboard.")

def create_and_display_chart(config, filtered_df):
    """Auxiliar para criar e exibir um gráfico com base na configuração."""
    try:
        if filtered_df.empty:
            st.warning("Não há dados disponíveis para gerar o gráfico.")
            return
            
        # Verificar se a configuração é válida
        if not config or not isinstance(config, dict):
            st.error("Configuração de gráfico inválida.")
            return
            
        # Verificar se o tipo de gráfico está definido
        if 'type' not in config:
            st.error("Tipo de gráfico não especificado na configuração.")
            return
            
        # Verificar se a coluna X está definida
        if 'x_col' not in config or config['x_col'] not in filtered_df.columns:
            st.error(f"Coluna do eixo X não encontrada: {config.get('x_col', 'não especificada')}")
            return
            
        # Criar gráfico de acordo com o tipo
        if config['type'] == "Histograma":
            fig = create_chart(
                filtered_df, 
                config['type'], 
                config['x_col'], 
                None, 
                config.get('color_col'), 
                config.get('title', "Histograma"),
                config.get('theme', 'plotly'),
                config.get('height', 500)
            )
        elif config['type'] == "Pizza":
            fig = create_chart(
                filtered_df, 
                config['type'], 
                config['x_col'], 
                config.get('y_col'), 
                config.get('color_col'), 
                config.get('title', "Gráfico de Pizza"),
                config.get('theme', 'plotly'),
                config.get('height', 500)
            )
        else:
            # Para outros tipos de gráfico, precisamos da coluna Y
            if 'y_col' not in config or config['y_col'] not in filtered_df.columns:
                st.error(f"Coluna do eixo Y não encontrada ou não especificada: {config.get('y_col', 'não especificada')}")
                return
                
            fig = create_chart(
                filtered_df, 
                config['type'], 
                config['x_col'], 
                config['y_col'], 
                config.get('color_col'), 
                config.get('title', f"Gráfico {config['type']}"),
                config.get('theme', 'plotly'),
                config.get('height', 500)
            )
        
        # Exibir o gráfico se foi criado com sucesso
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Não foi possível criar o gráfico. Verifique as configurações.")
    
    except Exception as e:
        st.error(f"Erro ao criar o gráfico: {str(e)}")
        # Adicionando mais detalhes para facilitar a depuração
        st.error(f"Tipo de gráfico: {config.get('type', 'não especificado')}")
        st.error(f"Coluna X: {config.get('x_col', 'não especificada')}")
        if config['type'] != "Histograma":
            st.error(f"Coluna Y: {config.get('y_col', 'não especificada')}") 