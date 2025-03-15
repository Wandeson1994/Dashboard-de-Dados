# Dashboard de Análise de Dados

Aplicação web criada com Streamlit para análise e visualização de dados, oferecendo recursos avançados de autenticação e personalização.

## Recursos Principais

- **Sistema de Autenticação Avançado**:
  - Login e senha tradicional
  - Cadastro de novas contas
  - Login via OAuth com Google e Facebook
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

3. Configure as APIs OAuth (opcional, apenas se for usar login com Google/Facebook):
   - Google:
     1. Acesse a [Google Cloud Console](https://console.cloud.google.com/)
     2. Crie um novo projeto
     3. Configure a tela de consentimento OAuth
     4. Crie credenciais OAuth 2.0 (tipo: Web application)
     5. Adicione `http://localhost:8501/callback` como URI de redirecionamento autorizado
     6. Anote o Client ID e Client Secret

   - Facebook:
     1. Acesse o [Facebook Developers](https://developers.facebook.com/)
     2. Crie um novo aplicativo
     3. Adicione o produto "Login do Facebook" ao seu aplicativo
     4. Em Configurações > Básico, anote o App ID e App Secret
     5. Em Configurações > Básico > URI de redirecionamento OAuth válidos, adicione `http://localhost:8501/callback`

4. Atualize as credenciais no arquivo `config/oauth_config.py`:
```python
# Substitua com seus dados reais
GOOGLE_CLIENT_ID = "seu-client-id-google"
GOOGLE_CLIENT_SECRET = "seu-client-secret-google"

FACEBOOK_CLIENT_ID = "seu-app-id-facebook"
FACEBOOK_CLIENT_SECRET = "seu-app-secret-facebook"
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
│   ├── oauth_config.py    # Configurações de OAuth
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

### Login via OAuth
A aplicação permite autenticação via:
- Google
- Facebook

Os usuários que entrarem por essas plataformas terão acesso como usuários padrão.

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