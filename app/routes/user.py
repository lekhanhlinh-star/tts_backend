from service.user import auth
from fastapi import APIRouter,Depends
from schemas.user import UserCreate
from utils.database import Session,get_db
from service.user import auth
user_router = APIRouter(prefix="/api/v1/user")

@user_router.post("/auth")
async def login_or_register(user: UserCreate, db: Session = Depends(get_db)):
    return await auth(user, db)