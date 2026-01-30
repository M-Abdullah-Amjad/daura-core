from typing import List, Optional, Union
from fastapi import Depends, HTTPException, status, Request
from app.modules.auth.dependencies.dependencies import get_current_user

class RoleChecker:
    """
    Dependency to enforce Role-Based Access Control (RBAC).
    
    Usage:
        @router.post("/", dependencies=[Depends(RoleChecker(["admin", "editor"]))])
        async def create_item():
            ...
    
    Checks 'realm_access.roles' and 'resource_access.{client}.roles'.
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: dict = Depends(get_current_user)):
        if not self.allowed_roles:
            return True

        user_roles = set()
        
        # 1. Check realm_access
        realm_access = user.get("realm_access", {})
        if realm_access and "roles" in realm_access:
            user_roles.update(realm_access["roles"])
            
        # 2. Check resource_access (optional, looks deep into structure)
        resource_access = user.get("resource_access", {})
        for client_data in resource_access.values():
            if "roles" in client_data:
                user_roles.update(client_data["roles"])
        
        # 3. Simple flat roles (fallback)
        if "roles" in user:
             user_roles.update(user["roles"])

        # Check intersection
        # If any allowed role is present, access is granted.
        # Logic can be enforcing ALL or ANY. Usually ANY is standard for lists.
        # The user example: @Roles({ roles: ['realm:Administrator'] }) implies ANY of these.
        
        if not any(role in user_roles for role in self.allowed_roles):
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. missing roles: {self.allowed_roles}"
            )
            
        return True


class PermissionChecker:
    """
    Dependency to enforce fine-grained permissions (Resource + Scope).
    
    Usage:
        @router.get("/", dependencies=[Depends(PermissionChecker(resource="photos", scope="view"))])
        async def get_photos():
            ...
            
    Expects Keycloak Authorization format in 'authorization' claim usually,
    OR a custom 'permissions' claim.
    
    Standard Keycloak RPT 'authorization' claim structure:
    "authorization": {
        "permissions": [
            {
                "rsid": "resource_id",
                "rsname": "resource_name",
                "scopes": ["scope1", "scope2"]
            }
        ]
    }
    """
    def __init__(self, resource: str, scope: Optional[str] = None):
        self.resource = resource
        self.scope = scope

    def __call__(self, user: dict = Depends(get_current_user)):
        # If no resource is defined, we might skip, but initialization requires it.
        
        permissions = []
        
        # Extract permissions from token
        # 1. Try standard 'authorization' claim (Keycloak UMA/RPT)
        authz = user.get("authorization", {})
        if authz and "permissions" in authz:
            permissions = authz["permissions"]
        
        # 2. Fallback: Check for flat 'permissions' list if configured differently
        elif "permissions" in user:
             permissions = user["permissions"]
             
        if not permissions:
             # If using Role-based inference for permissions, one might check roles here.
             # But strictly, if a Permission check is requested, and no permissions present -> Forbidden.
             # UNLESS the user wants to fallback to Roles. 
             # For enterprise cleanliness, we keeping it strict.
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permissions found in token"
            )

        has_permission = False
        
        for perm in permissions:
            # Check resource name (rsname) or resource id (rsid)
            # We compare against 'rsname' usually.
            rsname = perm.get("rsname")
            rsid = perm.get("rsid") # sometimes resource is passed as ID
            
            # Match Resource
            if rsname == self.resource or rsid == self.resource:
                # If scope is required, check it
                if self.scope:
                    scopes = perm.get("scopes", [])
                    if self.scope in scopes:
                        has_permission = True
                        break
                else:
                    # No scope required, just resource access
                    has_permission = True
                    break
        
        if not has_permission:
            detail = f"Missing permission for resource '{self.resource}'"
            if self.scope:
                detail += f" with scope '{self.scope}'"
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=detail
            )
            
        return True
