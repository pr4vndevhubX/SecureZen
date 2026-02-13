import os
import sys
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import jwt
from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# Import Utils
from utils.database import ThreatDatabase
from utils.auth_db import UserDatabase
from utils.wazuh_connector import WazuhConnector
from services.copilot_service import CopilotService

# Load Env
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

security = HTTPBearer()

# Models
class ChatRequest(BaseModel):
    message: str

class IOCAnalysisRequest(BaseModel):
    ioc: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Shared App Factory
def create_base_app(title: str):
    app = FastAPI(title=title, version="1.0.0")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

# Shared Helpers
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Shared DB instances (Singletons)
default_db = "data/wazuh_alerts.db"
if os.getenv("SECUREZEN_MODE") == "standalone":
    default_db = "data/syslog_alerts.db"

db_path = os.getenv("SECUREZEN_DB_PATH", os.path.join(project_root, default_db))
db = ThreatDatabase(db_path=db_path)
user_db = UserDatabase(db_path=os.path.join(project_root, "data/users.db"))
connector = WazuhConnector()
copilot = CopilotService(db_connector=db)

# Shared Routes
def register_shared_routes(app: FastAPI):
    @app.post("/api/auth/login")
    async def login(request: LoginRequest):
        user = user_db.verify_user(request.email, request.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token(data={"sub": user['email']})
        return {"access_token": token, "token_type": "bearer", "user": user}

    @app.post("/api/auth/register")
    async def register(request: RegisterRequest):
        try:
            user = user_db.create_user(request.email, request.password, request.full_name)
            return user
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/auth/verify")
    async def verify(email: str = Depends(verify_token)):
        user = user_db.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"user": user}

    @app.post("/api/copilot/chat")
    async def chat(request: ChatRequest, email: str = Depends(verify_token)):
        response = await copilot.get_response(request.message)
        return {"response": response}
