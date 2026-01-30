from fastapi.responses import JSONResponse

async def tokenSeparator(token: str) -> str:
    """Separates Bearer token from the 'Bearer ' prefix."""
    if not token or not token.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Authorization header missing or invalid"})
    
    if token.startswith("Bearer "):
        return token[7:]
    return token