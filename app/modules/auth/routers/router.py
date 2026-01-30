from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.modules.auth.services.service import (
    login,
    refresh_token,
    logout,
    register_user,
    forgot_password,
    reset_password,
    get_userinfo,
    introspect_token,
    update_profile,
    change_password,
    logout_revoke,
)
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
from app.modules.auth.dependencies.dependencies import get_current_user

router = APIRouter()
security = HTTPBearer()

@router.post("/login", response_model=TokenResponse)
def login_endpoint(credentials: LoginRequest):
    return login(credentials)

@router.post("/refresh", response_model=TokenResponse)
def refresh_endpoint(refresh_request: RefreshRequest):
    return refresh_token(refresh_request)

@router.post("/logout")
def logout_endpoint():
    return logout()

@router.post("/register")
def register_endpoint(user_data: RegisterRequest):
    return register_user(user_data)

@router.post("/forgot-password")
def forgot_password_endpoint(request: ForgotPasswordRequest):
    return forgot_password(request)

@router.post("/reset-password")
def reset_password_endpoint(request: ResetPasswordRequest):
    return reset_password(request)

@router.get("/userinfo", response_model=UserInfo)
def userinfo_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return get_userinfo(credentials.credentials)

@router.post("/introspect")
def introspect_endpoint(token: str):
    return introspect_token(token)

@router.put("/profile")
def profile_endpoint(
    profile_data: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("sub")  # Assuming sub is user id
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token")
    return update_profile(profile_data, user_id)

@router.post("/change-password")
def change_password_endpoint(
    password_data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token")
    return change_password(password_data, user_id)

@router.post("/logout-revoke")
def logout_revoke_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return logout_revoke(credentials.credentials)
