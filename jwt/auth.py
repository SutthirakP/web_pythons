from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from pwdlib import PasswordHash

router = APIRouter()

SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

password_hash = PasswordHash.recommended()
hashed = password_hash.hash("1234")

blacklist = set()

user = {
    "admin": {
        "username": "admin",
        "password": hashed
    }
}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    account = user.get(form_data.username)

    if not account or not password_hash.verify(form_data.password, account["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    print(account)
    
    expries = datetime.now(timezone.utc) + timedelta(minutes=20)
    
    token = jwt.encode( {
        "sub": account["username"],
        "exp": expries
    },
    SECRET_KEY, algorithm=ALGORITHM
    )
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token:str = Depends(oauth2_scheme)):
    
    if token in blacklist:
        raise HTTPException(status_code=401, detail="Token has been revoked")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
@router.get("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    blacklist.add(token)
    return {"message": "Logged out successfully"}