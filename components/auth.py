import streamlit as st
import yaml
import os.path
import streamlit_authenticator as stauth
import requests
import json
import uuid
from urllib.parse import urlencode
from config.oauth_config import (
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, GOOGLE_SCOPE,
    GOOGLE_AUTH_URL, GOOGLE_TOKEN_URL, GOOGLE_USER_INFO_URL,
    FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET, FACEBOOK_REDIRECT_URI, FACEBOOK_SCOPE,
    FACEBOOK_AUTH_URL, FACEBOOK_TOKEN_URL, FACEBOOK_USER_INFO_URL
)

# Caminho para o arquivo de configuração
CONFIG_PATH = "config/auth.yaml"

def load_config():
    """Carrega a configuração do arquivo YAML."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as file:
            config = yaml.safe_load(file)
        return config
    return None

def save_config(config):
    """Salva a configuração no arquivo YAML."""
    with open(CONFIG_PATH, 'w') as file:
        yaml.dump(config, file)

def initialize_session():
    """Inicializa as variáveis de sessão se não existirem."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'auth_source' not in st.session_state:
        st.session_state.auth_source = None
    if 'oauth_state' not in st.session_state:
        st.session_state.oauth_state = str(uuid.uuid4())

def login_form():
    """Renderiza o formulário de login com opções de autenticação."""
    initialize_session()
    
    if st.session_state.logged_in:
        return True
    
    st.title("Acesso ao Sistema")
    
    # Criamos abas para diferentes métodos de login
    tab1, tab2, tab3 = st.tabs(["Login", "Cadastro", "Login com Redes Sociais"])
    
    # 1. Login tradicional
    with tab1:
        config = load_config()
        if config:
            authenticator = stauth.Authenticate(
                config['credentials'],
                config['cookie']['name'],
                config['cookie']['key'],
                config['cookie']['expiry_days']
            )
            
            # Chamamos o método login sem tentar desempacotar seu retorno
            authenticator.login(location="main", key="login-auth-form")
            
            # Acessamos os valores do session_state
            authentication_status = st.session_state.get("authentication_status")
            name = st.session_state.get("name")
            username = st.session_state.get("username")
            
            if authentication_status:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.user_info = {
                    'name': config['credentials']['usernames'][username]['name'],
                    'role': config['credentials']['usernames'][username]['role']
                }
                st.session_state.auth_source = "traditional"
                st.rerun()
            elif authentication_status is False:
                st.error("Usuário ou senha incorretos")
            elif authentication_status is None:
                st.info("Por favor, insira suas credenciais")
    
    # 2. Formulário de cadastro
    with tab2:
        with st.form("signup_form"):
            st.subheader("Criar Nova Conta")
            new_username = st.text_input("Nome de usuário")
            new_name = st.text_input("Nome completo")
            new_email = st.text_input("Email")
            new_password = st.text_input("Senha", type="password")
            confirm_password = st.text_input("Confirme a senha", type="password")
            signup_submitted = st.form_submit_button("Cadastrar")
            
            if signup_submitted:
                if not (new_username and new_name and new_email and new_password):
                    st.error("Todos os campos são obrigatórios")
                elif new_password != confirm_password:
                    st.error("As senhas não coincidem")
                else:
                    config = load_config()
                    if config and new_username in config['credentials']['usernames']:
                        st.error("Nome de usuário já existe. Escolha outro.")
                    else:
                        # Vamos adicionar o novo usuário
                        if config is None:
                            # Cria uma configuração vazia se não existir
                            config = {
                                'credentials': {
                                    'usernames': {}
                                },
                                'cookie': {
                                    'expiry_days': 30,
                                    'key': 'analise_dados_auth',
                                    'name': 'analise_dados_cookie'
                                },
                                'preauthorized': {
                                    'emails': []
                                }
                            }
                        
                        # Gera o hash da senha
                        hasher = stauth.Hasher()
                        hashed_password = hasher.hash(new_password)
                        
                        # Adiciona o novo usuário
                        config['credentials']['usernames'][new_username] = {
                            'email': new_email,
                            'name': new_name,
                            'password': hashed_password,
                            'role': 'user'  # Por padrão, novos usuários são "user"
                        }
                        
                        # Salva a configuração atualizada
                        save_config(config)
                        
                        st.success("Cadastro realizado com sucesso! Faça login para continuar.")
                        st.rerun()
    
    # 3. Login com redes sociais
    with tab3:
        st.subheader("Login com redes sociais")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Login com Google", use_container_width=True):
                params = {
                    'client_id': GOOGLE_CLIENT_ID,
                    'redirect_uri': GOOGLE_REDIRECT_URI,
                    'scope': ' '.join(GOOGLE_SCOPE),
                    'response_type': 'code',
                    'state': st.session_state.oauth_state,
                    'access_type': 'offline',
                    'prompt': 'consent'
                }
                google_auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
                st.markdown(f'<meta http-equiv="refresh" content="0;url={google_auth_url}">', unsafe_allow_html=True)
        
        with col2:
            if st.button("Login com Facebook", use_container_width=True):
                params = {
                    'client_id': FACEBOOK_CLIENT_ID,
                    'redirect_uri': FACEBOOK_REDIRECT_URI,
                    'scope': ','.join(FACEBOOK_SCOPE),
                    'response_type': 'code',
                    'state': st.session_state.oauth_state
                }
                facebook_auth_url = f"{FACEBOOK_AUTH_URL}?{urlencode(params)}"
                st.markdown(f'<meta http-equiv="refresh" content="0;url={facebook_auth_url}">', unsafe_allow_html=True)
    
    # Verificar código de retorno OAuth na URL
    query_params = st.query_params.to_dict()
    
    if 'code' in query_params and 'state' in query_params:
        code = query_params['code'][0]
        state = query_params['state'][0]
        
        # Verificar que o estado corresponde (previne CSRF)
        if state == st.session_state.oauth_state:
            # Determinar qual provedor respondeu com base nos parâmetros retornados
            provider = "google" if "scope" in query_params else "facebook"
            
            if provider == "google":
                process_google_callback(code)
            else:
                process_facebook_callback(code)
            
            # Limpar parâmetros de URL após processamento
            st.query_params.clear()
            
    return st.session_state.logged_in

def process_google_callback(code):
    """Processa o retorno de autenticação do Google."""
    try:
        # Troca o código de autorização por um token de acesso
        token_response = requests.post(
            GOOGLE_TOKEN_URL,
            data={
                'code': code,
                'client_id': GOOGLE_CLIENT_ID,
                'client_secret': GOOGLE_CLIENT_SECRET,
                'redirect_uri': GOOGLE_REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
        )
        token_data = token_response.json()
        
        if 'access_token' not in token_data:
            st.error(f"Erro ao obter token: {token_data.get('error_description', 'Erro desconhecido')}")
            return
        
        # Obtém informações do usuário
        user_info_response = requests.get(
            GOOGLE_USER_INFO_URL,
            headers={'Authorization': f"Bearer {token_data['access_token']}"}
        )
        user_info = user_info_response.json()
        
        # Registra o usuário no sistema se ele ainda não existir
        register_oauth_user(
            username=f"google_{user_info['id']}",
            name=user_info['name'],
            email=user_info['email'],
            provider="google"
        )
        
        # Loga o usuário
        st.session_state.logged_in = True
        st.session_state.username = f"google_{user_info['id']}"
        st.session_state.user_info = {
            'name': user_info['name'],
            'role': 'user',
            'email': user_info['email'],
            'picture': user_info.get('picture', None)
        }
        st.session_state.auth_source = "google"
        st.rerun()
        
    except Exception as e:
        st.error(f"Erro ao processar autenticação Google: {str(e)}")

def process_facebook_callback(code):
    """Processa o retorno de autenticação do Facebook."""
    try:
        # Troca o código de autorização por um token de acesso
        token_response = requests.get(
            FACEBOOK_TOKEN_URL,
            params={
                'client_id': FACEBOOK_CLIENT_ID,
                'client_secret': FACEBOOK_CLIENT_SECRET,
                'redirect_uri': FACEBOOK_REDIRECT_URI,
                'code': code
            }
        )
        token_data = token_response.json()
        
        if 'access_token' not in token_data:
            st.error(f"Erro ao obter token: {token_data.get('error_description', 'Erro desconhecido')}")
            return
        
        # Obtém informações do usuário
        user_info_response = requests.get(
            FACEBOOK_USER_INFO_URL,
            params={'access_token': token_data['access_token']}
        )
        user_info = user_info_response.json()
        
        # Registra o usuário no sistema se ele ainda não existir
        register_oauth_user(
            username=f"facebook_{user_info['id']}",
            name=user_info['name'],
            email=user_info.get('email', f"fb_{user_info['id']}@placeholder.com"),
            provider="facebook"
        )
        
        # Loga o usuário
        st.session_state.logged_in = True
        st.session_state.username = f"facebook_{user_info['id']}"
        st.session_state.user_info = {
            'name': user_info['name'],
            'role': 'user',
            'email': user_info.get('email', f"fb_{user_info['id']}@placeholder.com"),
            'picture': user_info.get('picture', {}).get('data', {}).get('url', None) if 'picture' in user_info else None
        }
        st.session_state.auth_source = "facebook"
        st.rerun()
        
    except Exception as e:
        st.error(f"Erro ao processar autenticação Facebook: {str(e)}")

def register_oauth_user(username, name, email, provider):
    """Registra um usuário que se autenticou via OAuth."""
    config = load_config()
    
    if config is None:
        # Cria uma configuração vazia se não existir
        config = {
            'credentials': {
                'usernames': {}
            },
            'cookie': {
                'expiry_days': 30,
                'key': 'analise_dados_auth',
                'name': 'analise_dados_cookie'
            },
            'preauthorized': {
                'emails': []
            }
        }
    
    # Verifica se o usuário já existe
    if username not in config['credentials']['usernames']:
        # Gera uma senha aleatória - o usuário nunca vai usá-la 
        # pois sempre vai entrar via OAuth
        random_password = str(uuid.uuid4())
        hasher = stauth.Hasher()
        hashed_password = hasher.hash(random_password)
        
        # Adiciona o novo usuário
        config['credentials']['usernames'][username] = {
            'email': email,
            'name': name,
            'password': hashed_password,
            'role': 'user',  # Por padrão, novos usuários são "user"
            'provider': provider
        }
        
        # Salva a configuração atualizada
        save_config(config)

def logout():
    """Realiza o logout do usuário."""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_info = None
    st.session_state.auth_source = None
    st.rerun()

def login_required(func):
    """Decorador para garantir que o usuário esteja logado."""
    def wrapper(*args, **kwargs):
        initialize_session()
        if not st.session_state.logged_in:
            if not login_form():
                return
        return func(*args, **kwargs)
    return wrapper 