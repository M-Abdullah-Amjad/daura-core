from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.helpers.tokenhelper import tokenSeparator
from app.modules.auth.keycloak.keycloak import keycloak_openid

async def auth_middleware(request: Request, call_next):
    # Define paths to exclude from authentication
    excluded_paths = ["/auth", "/docs", "/redoc", "/openapi.json"]
    if any(request.url.path.startswith(path) for path in excluded_paths):
        return await call_next(request)

    # Get authorization header
    auth_header = request.headers.get("Authorization")
    
    tokenhelper_response = await tokenSeparator(auth_header)
    if isinstance(tokenhelper_response, JSONResponse):
        return tokenhelper_response
    token = tokenhelper_response
    try:
        # Introspect the token (assuming introspect is synchronous)
        token_info = keycloak_openid.introspect(token)
        
        if not token_info.get('active', False):
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})
        
    except Exception as e:
        print(f"Auth Middleware Error: {str(e)}")
        return JSONResponse(status_code=401, content={"detail": "Token validation failed"})
    
    # Proceed to the next middleware or route handler
    response = await call_next(request)
    return response