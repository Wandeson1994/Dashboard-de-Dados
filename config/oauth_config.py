"""
Configurações para autenticação OAuth.
"""

# Configurações do Google OAuth
GOOGLE_CLIENT_ID = "759973083046-ldmssmmegiarirn1vomf2qvdk6ou4rb6.apps.googleusercontent.com"  # Substitua pelo seu Client ID do Google
GOOGLE_CLIENT_SECRET = "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"  # Substitua pelo seu Client Secret do Google
GOOGLE_REDIRECT_URI = "https://dashboard-wandersolutions.streamlit.app"  # URL de redirecionamento após autenticação

# Configurações do Facebook OAuth
FACEBOOK_CLIENT_ID = "1672423616965359"  # Substitua pelo seu App ID do Facebook
FACEBOOK_CLIENT_SECRET = "f7b715501a2bab01f5ef3d19812c7047"  # Substitua pelo seu App Secret do Facebook
FACEBOOK_REDIRECT_URI = "https://dashboard-wandersolutions.streamlit.app"  # URL de redirecionamento após autenticação

# Escopos das permissões solicitadas
GOOGLE_SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email", 
    "https://www.googleapis.com/auth/userinfo.profile", 
    "openid"
]

FACEBOOK_SCOPE = ["email", "public_profile"]

# URL de autorização
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

FACEBOOK_AUTH_URL = "https://www.facebook.com/v12.0/dialog/oauth"
FACEBOOK_TOKEN_URL = "https://graph.facebook.com/v12.0/oauth/access_token"
FACEBOOK_USER_INFO_URL = "https://graph.facebook.com/me?fields=id,name,email,picture" 
