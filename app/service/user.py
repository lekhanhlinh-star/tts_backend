from utils.database import get_db,Session,pwd_context
from models.user import User
from schemas.user import UserCreate
from fastapi import Depends, HTTPException



async def auth(user ,db):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if not existing_user:
        hashed_password = pwd_context.hash(user.password)
        new_user = User(email=user.email, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"status": "success", "detail": {"uid": new_user.uid}}
    
    if not pwd_context.verify(user.password, existing_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"status": "success", "detail": {"uid": existing_user.uid}}

