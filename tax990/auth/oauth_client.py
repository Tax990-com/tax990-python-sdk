from __future__ import annotations

import time

import jwt

from tax990.errors.exceptions import AuthError
from tax990.http.http_client import HttpClient
from tax990.models.auth import GenerateJWSResponse, Tax990TokenResponse


class OAuthClient:
    """
    Implements the Tax990 two-step token flow (ANALYSIS.md §Authentication):
      1. Sign a JWS locally with HS256 (claims: iss/sub/aud/iat, key: client_secret)
      2. GET /Auth/GetTax990Token with `authentication: <JWS>` → RS256 access token
    """

    def __init__(
        self,
        http: HttpClient,
        client_id: str,
        client_secret: str,
        user_token: str,
    ) -> None:
        self._http = http
        self._client_id = client_id
        self._client_secret = client_secret
        self._user_token = user_token

    def sign_jws_locally(self) -> str:
        """Signs a JWS using HS256 with client_secret. Claims per ANALYSIS.md."""
        payload = {
            "iss": self._client_id,
            "sub": self._client_id,
            "aud": self._user_token,
            "iat": int(time.time()),
        }
        return jwt.encode(payload, self._client_secret, algorithm="HS256")

    async def generate_jws_from_server(self) -> str:
        """Calls POST /Auth/GenerateJWS to obtain JWS from the server."""
        data = await self._http.post(
            "/Auth/GenerateJWS",
            json={
                "ClientId": self._client_id,
                "ClientSecretId": self._client_secret,
                "UserToken": self._user_token,
            },
        )
        response = GenerateJWSResponse.model_validate(data)
        return response.response.JWSToken

    async def get_access_token(self) -> tuple[str, int]:
        """
        Returns (access_token, expires_in_seconds).
        Raises AuthError if the server returns an error in the response body.
        """
        jws = self.sign_jws_locally()
        data = await self._http.get(
            "/Auth/GetTax990Token",
            extra_headers={"authentication": jws},
        )
        response = Tax990TokenResponse.model_validate(data)
        if response.response.Errors is not None:
            raise AuthError(response.response.Errors.ErrorMessage)
        return response.response.AccessToken, response.response.ExpiresIn or 3600
