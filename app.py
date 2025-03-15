import streamlit as st
from pages.home import home_page
from pages.upload_page import upload_page
from pages.dashboard_page import dashboard_page
from components.auth import initialize_session, logout

# Configurações da página
st.set_page_config(
    page_title="Análise de Dados Interativa",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Inicializar variáveis de sessão
    initialize_session()
    
    # Sidebar para navegação
    with st.sidebar:
        st.title("📊 Analítica Visual")
        
        # Informações do usuário
        if st.session_state.logged_in:
            # Obter nome do usuário e papel
            user_name = st.session_state.user_info['name']
            user_role = st.session_state.user_info['role']
            
            # Verifica se o usuário foi autenticado via OAuth e tem uma imagem de perfil
            if 'picture' in st.session_state.user_info and st.session_state.user_info['picture']:
                st.image(st.session_state.user_info['picture'], width=100)
            
            # Exibir informações do usuário
            st.markdown(f"### Olá, {user_name}!")
            st.write(f"Perfil: **{user_role}**")
            
            # Exibir origem da autenticação
            if 'auth_source' in st.session_state and st.session_state.auth_source:
                auth_sources = {
                    'traditional': 'Login Tradicional',
                    'google': 'Google',
                    'facebook': 'Facebook'
                }
                auth_source = auth_sources.get(st.session_state.auth_source, 'Desconhecido')
                st.write(f"Login via: **{auth_source}**")
            
            # Menu de navegação
            st.subheader("Menu Principal")
            
            page = st.radio(
                "Navegue para:",
                ["Home", "Upload de Arquivos", "Dashboards"]
            )
            
            # Botão de logout
            if st.button("Logout"):
                logout()
        else:
            # Se não estiver logado, apenas mostra página de login
            page = "Home"
    
    # Renderizar a página selecionada
    if page == "Home":
        home_page()
    elif page == "Upload de Arquivos":
        upload_page()
    elif page == "Dashboards":
        dashboard_page()

if __name__ == "__main__":
    main() 