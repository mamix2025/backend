from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, sessionmaker

from fastapi import FastAPI
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from orm_models import (Manager, Area, Building, Entrance, Apartment, Resident, Plumbing,
                        Heating, Electrical, Request, Worker, Assignment, Material)
from datetime import datetime


app = FastAPI()
Base = declarative_base()
engine = create_engine('postgresql+psycopg2://user:1111@localhost:5432/management')

SessionLocal = sessionmaker(bind=engine)



class RegisterOut(BaseModel):
    success: bool
    user_id: Optional[int] = None
    message: str

class RegisterIn(BaseModel):
    login: str
    password: str
    phone: str
    full_name: str
    email: EmailStr


class Login(BaseModel):
    login: str
    password: str

class RequestsIn(BaseModel):
    manager_name: str

class RequestsOut(BaseModel):
    request_id: int
    address: str
    apartment_id: int
    type: str
    status: str
    created_at: datetime
    resident_name: str

class ListRequestsOut(BaseModel):
    requests: List[RequestsOut]
    total: int

class RequestsCreateIn(BaseModel):
    apartment_id: int
    type: str
    description: str

class RequestsCreateOut(BaseModel):
    success: bool
    request_id: Optional[int] = None

@app.post("/api/register", response_model=RegisterOut)
def register_user(user: RegisterIn):
    session = SessionLocal()
    try:
        new_user = Manager(login=user.login, hashed_password=user.password,
                           phone=user.phone, full_name=user.full_name, email=user.email)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return {
            "success": True,
            "user_id": new_user.manager_id,
            "message": "User registered successfully"
        }
    except IntegrityError as e:
        # Ошибка, если логин уже существует (нарушение уникальности)
        session.rollback()
        return {
            "success": False,
            "user_id": None,
            "message": "Login already exists"
        }
    except Exception as e:
        # Другие ошибки
        session.rollback()
        return {
            "success": False,
            "user_id": None,
            "message": f"Error: {str(e)}"
        }
    finally:
        session.close()





@app.post("/api/requests/create", response_model=RequestsCreateOut)
def create_request(req: RequestsCreateIn):
    session = SessionLocal()
    try:
        db_req = Request(apartment_id=req.apartment_id, type=req.type, description=req.description)
        session.add(db_req)
        session.commit()
        session.refresh(db_req)
        return {
            "success": True,
            "request_id": db_req.request_id
        }
    except Exception as e:
        session.rollback()
        return {
            "success": False,
            "request_id": None
        }
    finally:
        session.close()


@app.post("/api/requests", response_model=ListRequestsOut)
def filter_by_manager(manager_name: str):
    session = SessionLocal()
    pass

# @app.post("/api/login")



