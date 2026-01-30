from fastapi import APIRouter, Depends
from app.modules.auth.dependencies.dependencies import get_current_user

router = APIRouter(prefix="/protected", tags=["Protected"])

@router.get("/")
def protected_route(user=Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user": user["preferred_username"],
        "roles": user.get("realm_access", {}).get("roles", []),
    }