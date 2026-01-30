from keycloak import KeycloakOpenID
from app.core.config import settings

keycloak_openid = KeycloakOpenID(
    server_url=f"{settings.KEYCLOAK_URL}/",
    client_id=settings.KEYCLOAK_CLIENT_ID,
    realm_name=settings.KEYCLOAK_REALM,
    client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
)
