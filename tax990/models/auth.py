from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel


@dataclass
class StoredToken:
    access_token: str
    expires_at: float  # unix timestamp in milliseconds


class TokenErrorDetail(BaseModel):
    ErrorCode: str
    ErrorName: str
    ErrorMessage: str


class Tax990TokenData(BaseModel):
    AccessToken: str
    TokenType: Optional[str] = None
    ExpiresIn: Optional[int] = None
    Errors: Optional[TokenErrorDetail] = None


class Tax990TokenResponse(BaseModel):
    statusCode: int
    status: str
    message: str
    response: Tax990TokenData


class JWSResponseData(BaseModel):
    JWSToken: str


class GenerateJWSResponse(BaseModel):
    statusCode: int
    status: str
    message: str
    response: JWSResponseData


class AuthorizeTokenData(BaseModel):
    IsJWTAuthorized: bool
    UserToken: Optional[str] = None
    UserId: Optional[str] = None
    TokenType: Optional[str] = None
    UnAuthorizeReason: Optional[str] = None


class AuthorizeTokenResponse(BaseModel):
    statusCode: int
    status: str
    message: str
    response: AuthorizeTokenData
