from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    firstName: str
    lastName: str
    password: str


class ForgotPasswordRequest(BaseModel):
    username: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class UpdateProfileRequest(BaseModel):
    firstName: str = None
    lastName: str = None
    email: str = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str = None
    expires_in: int = None
    refresh_expires_in: int = None
    token_type: str = "Bearer"


class UserInfo(BaseModel):
    sub: str
    name: str = None
    given_name: str = None
    family_name: str = None
    email: str = None
    preferred_username: str = None