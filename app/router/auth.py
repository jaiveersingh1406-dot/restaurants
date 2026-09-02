from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schema.schema import (
    signup as SignupSchema,
    login as LoginSchema,
    change_password as ChangePasswordSchema,
    profile_update as ProfileUpdateSchema,
)
from app.service.service import (
    get_signup,
    authenticate,
    change_password,
    check_email_exists,
    update_user_profile,
    get_profile,
)
from app.core.security import create_access_token, decode_access_token

router = APIRouter()

bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/auth/check-email")
def check_email(payload: dict):
    email = (payload.get("email") or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    return {"exists": check_email_exists(email)}


@router.post("/signup")
def signup(user: SignupSchema):
    get_signup(user.username, user.email, user.password)
    return {"message": "User signed up successfully"}


@router.post("/login")
def login(user: LoginSchema):
    requested_role = "admin" if user.role == "admin" else None

    account = None

    for role in ([requested_role] if requested_role else ["user", "admin"]):
        account = authenticate(user.email, user.password, role)
        if account:
            break

    if account is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(account["email"], account["role"])

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": account,
    }


@router.get("/auth/me")
def auth_me(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_access_token(credentials.credentials)

    if payload is None:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")

    profile = get_profile(payload["sub"], payload["role"])
    if profile is None:
        raise HTTPException(status_code=404, detail="User not found")

    return profile


@router.post("/auth/change-password")
def update_password(
    body: ChangePasswordSchema,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_access_token(credentials.credentials)

    if payload is None:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")

    return change_password(
        payload["sub"],
        payload["role"],
        body.old_password,
        body.new_password,
    )


@router.put("/auth/profile")
def update_profile(
    body: ProfileUpdateSchema,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_access_token(credentials.credentials)

    if payload is None:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")

    if payload["role"] != "user":
        raise HTTPException(status_code=403, detail="Only customer accounts can update their profile")

    updated = update_user_profile(payload["sub"], body.phone)

    return updated
