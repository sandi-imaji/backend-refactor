from fastapi import APIRouter,HTTPException,Depends
from sqlmodel import Session
from app.database.schemas import ModelResponseSchema
from app.database.db import get_session
from app.database.orm import ModelML,Dataset

modelRouter = APIRouter()


@modelRouter.get("/models")
async def get_models(db:Session=Depends(get_session)):
  q = db.query(ModelML).all()





