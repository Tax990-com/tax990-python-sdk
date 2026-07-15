from __future__ import annotations

from typing import Any

VALID_CONFIG: dict[str, str] = {
    "client_id": "test-client-id",
    "client_secret": "test-client-secret-32-chars-long!!",
    "user_token": "test-user-token",
    "environment": "sandbox",
}

TOKEN_RESPONSE: dict[str, Any] = {
    "statusCode": 200,
    "status": "OK",
    "message": "Successful API call.",
    "response": {
        "AccessToken": "eyJhbGciOiJSUzI1NiJ9.access.signature",
        "TokenType": "Bearer",
        "ExpiresIn": 3600,
        "Errors": None,
    },
}

JWS_RESPONSE: dict[str, Any] = {
    "statusCode": 200,
    "status": "Success",
    "message": "JWS Generated Successfully",
    "response": {"JWSToken": "eyJhbGciOiJIUzI1NiJ9.test.signature"},
}

UNAUTHORIZED_RESPONSE: dict[str, Any] = {
    "statusCode": 401,
    "status": "Unauthorized",
    "message": "Unauthorized",
    "response": {
        "AccessToken": "",
        "TokenType": None,
        "ExpiresIn": None,
        "Errors": {
            "ErrorCode": "401-ERR-03",
            "ErrorName": "Authentication",
            "ErrorMessage": "Invalid credentials",
        },
    },
}
