from fastapi import APIRouter,HTTPException,Depends
from sqlmodel import Session
from app.database.schemas import ModelResponseSchema
from app.database.db import get_session
from app.database.orm import ModelML,Dataset

modelRouter = APIRouter()

@modelRouter.get("/dataset/models")
async def get_models_req(name,db:Session=Depends(get_session)):
  q = Dataset.get_by_name(name,db)
  return q

@modelRouter.get("/models")
async def get_all_models_req(name,db:Session=Depends(get_session)):
  q = db.query(ModelML).all()
  return q

@modelRouter.get("/model")
async def get_by_name_req(name,db):
  q = db.query(ModelML).all()
  return q








