# Dashboard de Análise de Dados

Aplicação web criada com Streamlit para análise e visualização de dados, oferecendo recursos de autenticação e personalização.

## Recursos Principais

- **Sistema de Autenticação**:
  - Login e senha tradicional
  - Cadastro de novas contas
  - Gerenciamento de sessões seguro

- **Análise de Dados**:
  - Upload de arquivos CSV
  - Processamento e limpeza de dados
  - Visualizações interativas
  - Filtros dinâmicos para análise aprofundada

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd <nome-da-pasta>
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Executando a Aplicação

```bash
streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501`.

## Estrutura do Projeto

```
📁 projeto/
│
├── 📁 arquivos_enviados/   # Armazenamento dos arquivos enviados
├── 📁 components/          # Componentes reutilizáveis
│   ├── auth.py            # Sistema de autenticação
│   ├── dashboard.py       # Componentes de visualização
│   └── file_processor.py  # Processamento de arquivos
│
├── 📁 config/              # Configurações
│   ├── auth.yaml          # Dados dos usuários (YAML)
│   └── users.py           # Usuários e autenticação
│
├── 📁 data/                # Dados processados
│
├── 📁 pages/               # Páginas da aplicação
│   ├── home.py            # Página inicial
│   ├── upload_page.py     # Página de upload
│   └── dashboard_page.py  # Página de dashboards
│
├── app.py                 # Arquivo principal
└── requirements.txt       # Dependências
```

## Sistema de Autenticação

### Login Tradicional
O sistema permite login e senha usando as credenciais padrão:
- **Usuário:** admin, **Senha:** admin123 (administrador)
- **Usuário:** usuario, **Senha:** senha123 (usuário padrão)

### Cadastro de Novos Usuários
Os usuários podem se cadastrar fornecendo:
- Nome de usuário
- Nome completo
- Email
- Senha

## Gerenciamento de Usuários

Para alterar as configurações de usuários, você pode:

1. Editar manualmente o arquivo `config/auth.yaml`
2. Usar a interface de cadastro para adicionar novos usuários

## Contribuição

Sinta-se à vontade para contribuir com este projeto.

## Licença

Este projeto é licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Fluxo de Trabalho

1. Faça login na aplicação
2. Acesse a página "Upload de Arquivos" para enviar seus arquivos CSV
3. Processe os arquivos para análise
4. Na página "Dashboards", selecione um arquivo processado
5. Crie visualizações interativas usando diferentes tipos de gráficos
6. Utilize os filtros para ajustar suas visualizações

## Requisitos do Sistema

- Python 3.8+
- Streamlit 1.27.0+
- Pandas 2.0.3+
- Plotly 5.16.1+ 