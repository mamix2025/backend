from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, Session

from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from orm_models import (Manager, Area, Building, Entrance, Apartment, Resident, Plumbing,
                        Heating, Electrical, Request, Worker, Assignment, Material, Status)
from config import engine

from datetime import datetime, timedelta
import jwt
from jwt import ExpiredSignatureError, PyJWTError
import bcrypt

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
SessionLocal = sessionmaker(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

# JWT настройки
SECRET_KEY = "bayden"  # Замените на безопасный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


# Зависимость для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


class LoginIn(BaseModel):
    login: str
    password: str


class LoginOut(BaseModel):
    success: bool
    token: str


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
    resident_id: int
    type: str
    description: str


class RequestsCreateOut(BaseModel):
    success: bool
    request_id: Optional[int] = None


@app.post("/api/register", response_model=RegisterOut, description="Register a new manager with hashed password")
def register_user(user: RegisterIn, db: Session = Depends(get_db)):
    try:
        # Хэширование пароля
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        # Создание нового пользователя с хэшированным паролем
        new_user = Manager(
            login=user.login,
            hashed_password=hashed_password.decode('utf-8'),  # Сохраняем как строку
            phone=user.phone,
            full_name=user.full_name,
            email=user.email
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {
            "success": True,
            "user_id": new_user.manager_id,
            "message": "User registered successfully"
        }
    except IntegrityError as e:
        db.rollback()
        return {
            "success": False,
            "user_id": None,
            "message": "Login or email already exists"
        }
    except Exception as e:
        db.rollback()
        print(f"Error during registration: {str(e)}")
        return {
            "success": False,
            "user_id": None,
            "message": f"Registration failed due to a server error: {str(e)}"
        }

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        manager_id: int = payload.get("sub")
        if manager_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен1")
        manager = db.query(Manager).filter(Manager.manager_id == manager_id).first()
        manager_id = int(manager_id)
        if not manager:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Менеджер не найден")
        return manager_id
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Срок действия токена истек")
    except PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен2")


@app.post("/api/requests/create", response_model=RequestsCreateOut)
def create_request(request: RequestsCreateIn, db: Session = Depends(get_db), manager_id: int = Depends(get_current_user)):
    # Проверка существования apartment_id
    apartment = db.query(Apartment).filter(Apartment.apartment_id == request.apartment_id).first()
    if not apartment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apartment not found")
        # Проверка существования resident_id
    resident = db.query(Resident).filter(Resident.resident_id == request.resident_id).first()
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")
    try:
        db_req = Request(apartment_id=request.apartment_id, resident_id=request.resident_id, type=request.type,
                         description=request.description, status_id=1)
        db.add(db_req)
        db.commit()
        db.refresh(db_req)
        return {
            "success": True,
            "request_id": db_req.request_id
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "request_id": None
        }


@app.post("/api/requests", response_model=ListRequestsOut)
def filter_by_manager(manager_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    result = (
        db.query(Request.request_id, Building.address, Apartment.apartment_id, Status.status_name, Request.type,
                 Request.created_at, Resident.full_name)
        .join(Apartment, Request.apartment_id == Apartment.apartment_id)
        .join(Entrance, Apartment.entrance_id == Entrance.entrance_id)
        .join(Building, Entrance.building_id == Building.building_id)
        .join(Area, Building.area_id == Area.area_id)
        .join(Status, Request.status_id == Status.status_id)
        .join(Resident, Request.resident_id == Resident.resident_id)
        .filter(Area.manager_id == manager_id)
        .all()
    )
    output = [
        RequestsOut(
            request_id=r.request_id,
            address=r.address,
            apartment_id=r.apartment_id,
            type=r.type,
            status=r.status_name,
            created_at=r.created_at,
            resident_name=r.full_name if r.full_name else "Не указан"
        ) for r in result
    ]
    print(output)
    return ListRequestsOut(requests=output, total=len(output))


# Endpoint для логина
@app.post("/api/login", response_model=LoginOut, include_in_schema=True)
def login_manager(request: LoginIn, db: Session = Depends(get_db)):
    # Поиск пользователя по логину
    manager = db.query(Manager).filter(Manager.login == request.login).first()
    # Проверка, существует ли пользователь
    if not manager:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password"
        )

    # Проверка пароля
    if not bcrypt.checkpw(
            request.password.encode('utf-8'),
            manager.hashed_password.encode('utf-8')
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password"
        )

    # Создание JWT-токена
    access_token = create_access_token(data={"sub": str(manager.manager_id)})

    return {"success": True, "token": access_token}
