import hashlib

def make_password_hash(password):
    """Cria um hash simples da senha fornecida."""
    return hashlib.sha256(password.encode()).hexdigest()

# Em um sistema real, você usaria um banco de dados
# Aqui usamos um dicionário para simplicidade
USERS = {
    "admin": {
        "password": make_password_hash("admin123"),
        "name": "Administrador",
        "role": "admin"
    },
    "usuario": {
        "password": make_password_hash("senha123"),
        "name": "Usuário Padrão",
        "role": "user"
    }
}

def verify_password(username, password):
    """Verifica se as credenciais estão corretas."""
    if username not in USERS:
        return False
    
    password_hash = make_password_hash(password)
    return password_hash == USERS[username]["password"]

def get_user_info(username):
    """Retorna informações do usuário."""
    if username in USERS:
        user_info = USERS[username].copy()
        user_info.pop("password")  # Não retorne a senha
        return user_info
    return None 