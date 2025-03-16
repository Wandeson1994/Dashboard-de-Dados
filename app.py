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
        if st.session_state.logged_in and st.session_state.user_info is not None:
            # Obter nome do usuário e papel
            user_name = st.session_state.user_info['name']
            user_role = st.session_state.user_info['role']
            
            # Exibir informações do usuário
            st.markdown(f"### Olá, {user_name}!")
            st.write(f"Perfil: **{user_role}**")
            
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