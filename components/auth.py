import streamlit as st
import yaml
import os.path
import streamlit_authenticator as stauth

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

def login_form():
    """Renderiza o formulário de login com opções de autenticação."""
    initialize_session()
    
    if st.session_state.logged_in:
        return True
    
    st.title("Acesso ao Sistema")
    
    # Criamos abas para diferentes métodos de login
    tab1, tab2 = st.tabs(["Login", "Cadastro"])
    
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
    
    return st.session_state.logged_in

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