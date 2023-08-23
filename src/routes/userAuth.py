from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional
from src.models.models import User
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import json
import jwt
from src.services.userAuth import signup, get_token, get_user, email_exists, username_exists, get_password_hash, authenticate, create_access_token, get_current_user

ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

class Token(BaseModel):
    access_token: str
    token_type: str
    user: str


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return get_token(form_data.username, form_data.password)
