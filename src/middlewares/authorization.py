from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from src.common.token.JwtService import JwtTokenService
from src.common.token.constants import TOKEN_TYPES

def require_access_token(
        request: Request,
        tokenService: Annotated[JwtTokenService, Depends(JwtTokenService)],
        ) -> dict:
    token = request.cookies.get("access_token")


    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    payload = tokenService.verify(token=token)
    if payload.get("type") != TOKEN_TYPES.ACCESS.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    return payload

def require_role(required_role: str):
    def role_checker(
        current_user: Annotated[dict, Depends(require_access_token)],
    ) -> dict:
        if (current_user["role"] != required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{required_role} access required",
            )

        return current_user

    return role_checker
