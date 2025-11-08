from fastapi import APIRouter,HTTPException,Depends
from sqlmodel import Session
from app.database.schemas import ModelResponseSchema,InferenceRequestSchema
from app.routes.dataset import check_integrity_dataset
from app.database.db import get_session
from app.database.orm import ModelML,Dataset

modelRouter = APIRouter()

@modelRouter.get("/dataset/model/initiate")
async def get_models_req(name,db:Session=Depends(get_session)):
  q = Dataset.get_by_name(name,db)

@modelRouter.get("/model/inference")
async def inference(payload:InferenceRequestSchema,db:Session=Depends(get_session)):
  q = Dataset.get_by_name(payload.dataset_name,db)
  check_integrity_dataset(q)

@modelRouter.get("/model")
async def get_by_name_req(name,db):
  q = db.query(ModelML).all()
  return q








