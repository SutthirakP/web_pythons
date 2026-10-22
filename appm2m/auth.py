import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .database import get_db
from .models import UserDB
from .rate_limit import login_limiter
from .schemas import UserRegister, UserResponse

router = APIRouter()

SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


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
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    account = db.query(UserDB).filter(UserDB.username == form_data.username).first()

    if not account or not verify_password(form_data.password, account.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = jwt.encode(
        {"sub": account.username},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    # JWT is stateless - the server holds no session to destroy. This endpoint
    # just confirms the token was valid; the client is responsible for
    # discarding it (that's the actual "log out" step).
    return {"message": f"Logged out {current_user['username']}"}
