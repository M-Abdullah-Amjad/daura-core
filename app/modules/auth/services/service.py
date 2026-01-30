from fastapi import HTTPException
from pydantic import BaseModel
import requests
from app.core.config import settings
from app.modules.auth.schemas.schema import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UpdateProfileRequest,
    ChangePasswordRequest,
    TokenResponse,
    UserInfo,
)
from app.shared.exceptions.exceptions import AuthenticationError, ValidationError, NotFoundError

# Use settings config
KEYCLOAK_URL = settings.KEYCLOAK_URL
KEYCLOAK_REALM = settings.KEYCLOAK_REALM
KEYCLOAK_CLIENT_ID = settings.KEYCLOAK_CLIENT_ID
KEYCLOAK_CLIENT_SECRET = settings.KEYCLOAK_CLIENT_SECRET

def login(credentials: LoginRequest) -> TokenResponse:
    """
    Custom login endpoint that validates credentials against Keycloak
    and returns tokens without showing Keycloak UI
    """
    token_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    print("Token URL:", token_url)
    
    # Use Direct Access Grant (Resource Owner Password Credentials)
    data = {
        "grant_type": "password",
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
        "username": credentials.username,
        "password": credentials.password,
        "scope": "openid profile email"
    }

    response = requests.post(token_url, data=data)
    
    if response.status_code != 200:
        raise AuthenticationError(
            detail="Invalid credentials",
            error_code="INVALID_CREDENTIALS"
        )

    tokens = response.json()
    return TokenResponse(**tokens)


# Optional refresh token endpoint
def refresh_token(refresh_request: RefreshRequest) -> TokenResponse:
    """
    Refresh access token using refresh token
    """
    token_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
        "refresh_token": refresh_request.refresh_token
    }
    response = requests.post(token_url, data=data)
    
    if response.status_code != 200:
        raise ValidationError(
            detail="Refresh token is invalid or expired",
            error_code="INVALID_REFRESH_TOKEN"
        )
    
    tokens = response.json()
    return TokenResponse(**tokens)


def logout():
    """
    Logout endpoint - client should discard tokens
    """
    return {"message": "Logged out successfully"}


# User registration endpoint (requires admin permissions)
def register_user(user_data: RegisterRequest):
    """
    Register a new user in Keycloak
    Requires admin client or appropriate permissions
    """
    # First, get admin token (assuming admin client is configured)
    admin_token_url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
    admin_data = {
        "grant_type": "client_credentials",
        "client_id": KEYCLOAK_CLIENT_ID,  # Assuming this client has admin permissions
        "client_secret": KEYCLOAK_CLIENT_SECRET,
    }
    
    admin_response = requests.post(admin_token_url, data=admin_data)
    if admin_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get admin token")
    
    admin_token = admin_response.json().get("access_token")
    
    # Create user
    user_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users"
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    
    user_payload = {
        "username": user_data.username,
        "email": user_data.email,
        "firstName": user_data.firstName,
        "lastName": user_data.lastName,
        "enabled": True,
        "credentials": [{"type": "password", "value": user_data.password, "temporary": False}]
    }
    
    response = requests.post(user_url, json=user_payload, headers=headers)
    if response.status_code == 201:
        return {"message": "User registered successfully"}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


# Forgot password endpoint
def forgot_password(request: ForgotPasswordRequest):
    """
    Initiate password reset for a user
    This sends an email to the user with reset instructions
    """
    # Get admin token
    admin_token_url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
    admin_data = {
        "grant_type": "client_credentials",
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
    }
    
    admin_response = requests.post(admin_token_url, data=admin_data)
    if admin_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get admin token")
    
    admin_token = admin_response.json().get("access_token")
    
    # Find user by username
    user_search_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users"
    headers = {"Authorization": f"Bearer {admin_token}"}
    params = {"username": request.username}
    
    search_response = requests.get(user_search_url, headers=headers, params=params)
    if search_response.status_code != 200 or not search_response.json():
        raise NotFoundError(
            detail="User not found",
            error_code="USER_NOT_FOUND"
        )
    
    user_id = search_response.json()[0]["id"]
    
    # Send password reset email
    reset_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user_id}/execute-actions-email"
    actions = ["UPDATE_PASSWORD"]
    
    response = requests.put(reset_url, json=actions, headers=headers)
    if response.status_code == 204:
        return {"message": "Password reset email sent"}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


# Reset password endpoint (after user clicks link in email)
def reset_password(request: ResetPasswordRequest):
    """
    Reset password using token from email
    """
    # This would typically be handled by Keycloak's built-in reset flow
    # For API, we can use the token to update password
    # But this requires parsing the token or using the reset flow
    
    # For simplicity, this endpoint assumes the token is valid and updates password
    # In practice, you'd validate the token first
    return {"message": "Password reset functionality - implement token validation"}


# Get user info
def get_userinfo(token: str) -> UserInfo:
    """
    Get user information from access token
    """
    userinfo_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/userinfo"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(userinfo_url, headers=headers)
    if response.status_code == 200:
        return UserInfo(**response.json())
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to get user info")


# Token introspection
def introspect_token(token: str):
    """
    Introspect access token to check validity and get claims
    """
    introspect_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token/introspect"
    data = {
        "token": token,
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
    }
    
    response = requests.post(introspect_url, data=data)
    return response.json()


# Update user profile
def update_profile(profile_data: UpdateProfileRequest, user_id: str):
    """
    Update user profile information
    """
    # Get admin token
    admin_token_url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
    admin_data = {
        "grant_type": "client_credentials",
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
    }
    
    admin_response = requests.post(admin_token_url, data=admin_data)
    if admin_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get admin token")
    
    admin_token = admin_response.json().get("access_token")
    
    user_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user_id}"
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    
    update_payload = {}
    if profile_data.firstName:
        update_payload["firstName"] = profile_data.firstName
    if profile_data.lastName:
        update_payload["lastName"] = profile_data.lastName
    if profile_data.email:
        update_payload["email"] = profile_data.email
    
    response = requests.put(user_url, json=update_payload, headers=headers)
    if response.status_code == 204:
        return {"message": "Profile updated successfully"}
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to update profile")


# Change password
def change_password(password_data: ChangePasswordRequest, user_id: str):
    """
    Change user password
    """
    # Get admin token
    admin_token_url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
    admin_data = {
        "grant_type": "client_credentials",
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
    }
    
    admin_response = requests.post(admin_token_url, data=admin_data)
    if admin_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get admin token")
    
    admin_token = admin_response.json().get("access_token")
    
    reset_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user_id}/reset-password"
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    
    reset_payload = {
        "type": "password",
        "value": password_data.new_password,
        "temporary": False
    }
    
    response = requests.put(reset_url, json=reset_payload, headers=headers)
    if response.status_code == 204:
        return {"message": "Password changed successfully"}
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to change password")


# Logout with token revocation
def logout_revoke(token: str):
    """
    Logout and revoke tokens
    """
    revoke_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/revoke"
    data = {
        "token": token,
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
    }
    
    response = requests.post(revoke_url, data=data)
    if response.status_code == 200:
        return {"message": "Logged out and tokens revoked"}
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to revoke token")
