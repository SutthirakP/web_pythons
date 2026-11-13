from typing import Annotated

import bcrypt
import jwt
from fastapi import APIRouter, Cookie, Depends, Form, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .database import get_db
from .models import UserDB
from .rate_limit import login_limiter
from .schemas import UserRegister, UserResponse
from .session import (
    REMEMBER_SECONDS,
    SESSION_COOKIE,
    create_session,
    delete_session,
    read_session,
)

router = APIRouter()

SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"

# auto_error=False: no Bearer header is fine, the session cookie may log you in instead
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

SessionCookie = Annotated[str | None, Cookie(alias=SESSION_COOKIE)]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


@router.post("/register", response_model=UserResponse)
async def register(user: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(UserDB).filter(UserDB.username == user.username).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user.username}' already exists",
        )

    db_user = UserDB(
        username=user.username,
        hashed_password=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", dependencies=[Depends(login_limiter)])  # 5 tries/minute, counted in Redis
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    remember: Annotated[bool, Form()] = False,  # the "Remember me" checkbox
):
    account = db.query(UserDB).filter(UserDB.username == form_data.username).first()

    if not account or not verify_password(form_data.password, account.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # 1) cookie session - the browser remembers the login by itself (catalog page uses this)
    session_id = await create_session(
        request.app.state.redis, account.id, account.username, remember
    )
    response.set_cookie(
        key=SESSION_COOKIE,
        value=session_id,
        # ticked: keep for 7 days / not ticked: None = session cookie, gone when the browser closes
        max_age=REMEMBER_SECONDS if remember else None,
        httponly=True,  # JavaScript can't read it -> an XSS bug can't steal it
        samesite="lax",  # not sent on cross-site form posts (basic CSRF protection)
    )

    # 2) JWT - still returned for /docs "Authorize" and other clients
    token = jwt.encode(
        {"sub": account.username},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": account.id, "username": account.username, "remember": remember},
    }


async def get_current_user(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    session_id: SessionCookie = None,
):
    """Logged in = a valid Bearer token OR a valid session cookie."""
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username}

    session = await read_session(request.app.state.redis, session_id)
    if session is not None:
        return {"username": session["username"], "user_id": session["user_id"]}

    raise HTTPException(
        status_code=401,
        detail="Not logged in",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.get("/me")
async def me(request: Request, session_id: SessionCookie = None):
    """Who am I, according to my cookie? The page calls this on load to restore the login."""
    session = await read_session(getattr(request.app.state, "redis", None), session_id)
    if session is None:
        raise HTTPException(status_code=401, detail="Not logged in")
    return {
        "id": session["user_id"],
        "username": session["username"],
        "remember": session.get("remember", False),
        "logged_in": True,
    }


@router.post("/logout")
async def logout(request: Request, response: Response, session_id: SessionCookie = None):
    # delete the server-side session AND tell the browser to drop the cookie
    await delete_session(getattr(request.app.state, "redis", None), session_id)
    response.delete_cookie(key=SESSION_COOKIE, httponly=True, samesite="lax")
    return {"message": "Logged out"}
