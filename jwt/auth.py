from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt

router = APIRouter()

SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

user = {
    "admin": {
        "username": "admin",
        "password": "1234"
    }
}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    account = user.get(form_data.username)

    if not account or account["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    print(account)
    
    token = jwt.encode( {
        "sub": account["username"]
    },
    SECRET_KEY, algorithm=ALGORITHM
    )
    return {"access_token": token, "token_type": "bearer"}