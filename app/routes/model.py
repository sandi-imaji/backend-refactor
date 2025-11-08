from fastapi import HTTPException
from app.database.orm import Dataset,ModelML
from app.database.schemas import StatusProcess
from app.config import Config
import os

def check_dataset_pretrained(dataset:Dataset):
  if not dataset.top_model: raise HTTPException(status_code=404,detail="Dataset is not trained !")
  if not dataset.models: raise HTTPException(status_code=404,detail="Dataset not found models")
  for m in dataset.models:
    if not m.is_active: raise HTTPException(status_code=500,detail=f"Model : {m.algorithm} is not active")
    if m.status != StatusProcess.SUCCESS_TRAIN: raise HTTPException(status_code=500,detail=f"Model : {m.algorithm} is not TRAIN | Status : {m.status}")
    pathfile = Config.dir/f"{m.path}.pkl"
    if not os.path.exists(pathfile): raise HTTPException(status_code=500,detail=f"Model : {m.algorithm} file is not found")


def inference(dataset:Dataset):pass

def auto_inference(dataset:Dataset):pass
