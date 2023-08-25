from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
from fastapi import HTTPException, status, Depends
from src.models.models import User
import json
import os
from dotenv import load_dotenv

ACCESS_TOKEN_EXPIRE_MINUTES = 120

def email_exists(email):
    try:
        user = User.objects.get(email=email)
        return True
    except User.DoesNotExist:
        return False

def username_exists(username):
    try:
        user = User.objects.get(username=username)
        return True
    except User.DoesNotExist:
        return False


class NewUser(BaseModel):
    email: str
    username: str
    password: str

def signup(newUser: NewUser):
    if email_exists(newUser.email):
        print("Admin already Registered")
        raise HTTPException(status_code=400, detail="Email already registered")
    elif username_exists(newUser.username):
        print("Admin already registered")
        raise HTTPException(status_code=400, detail="Username already registered")

    user = User(email = newUser.email, username = newUser.username, password = get_password_hash(newUser.password))
    user.save()
    print("User Created")
    return {"message" : "User Successfully created!"}


crypt_context = CryptContext(schemes = ["sha256_crypt", "md5_crypt"])

def get_password_hash(password):
    return crypt_context.hash(password)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

SECRET_KEY = "fd68bbcc397ff21d9073b18ef8d3ba6df9dc22fa68c8a827dfbeef7fc7af7f50"

ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def get_token(username:str, password:str):
    if authenticate(username, password):
        user_data = get_user(username)
        
        access_token = create_access_token(
        data={
            "sub": user_data["_id"]["$oid"],
            "username": user_data["username"],
            "email": user_data["email"]
        },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
        return {
            "access_token": access_token, 
            "token_type": "bearer", 
            "user": user_data["_id"]["$oid"],
            "message" : "Credentials Verified"
        }
    else:
        raise HTTPException(
            status_code = 400, detail= "Incorrect username or password"
        )

def verify_password(plain_password, hashed_password):
    return crypt_context.verify(plain_password, hashed_password)

def authenticate(email, password):
    try:
        user = get_user(email)
        password_check = verify_password(password, user['password'])
        return password_check
    except User.DoesNotExist:
        return False


class TokenData(BaseModel):
    username: Optional[str] = None
    userId: Optional[str] = None
    email: Optional[str] = None

def get_user(username :str):
    try:
        user = json.loads(User.objects.get(username = username).to_json())
        return user
    except User.DoesNotExist:
        return None        

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers = {"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        userId: int = payload.get("sub")
        email: str = payload.get("email")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, userId=userId, email=email)
    except:
        raise credentials_exception
    return token_data

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )