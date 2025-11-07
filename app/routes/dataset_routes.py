from fastapi import HTTPException,Depends,BackgroundTasks,APIRouter
from app.database.db import get_session
from sqlmodel import Session
from app.database.orm import Dataset
from app.database.schemas import DatasetRequestSchema,TaskType,DatasetResponseSchema
from app.routes import dataset
from app.pull import pulling
from app.dummy import create_dummy

datasetRouter = APIRouter()

@datasetRouter.get("/datasets")
async def get_dataset_req(db:Session = Depends(get_session)):
  datasets = Dataset.get_all(db)
  if not datasets: raise HTTPException(status_code=404,detail="Datasets is empty")
  return Dataset.to_responses(datasets,db)

@datasetRouter.get("/datasets/filter")
async def get_dataset_by_task_type_req(task_type:str,db:Session = Depends(get_session)):
  dataset = Dataset.get_by_task_type(task_type,db)
  return Dataset.to_responses(dataset,db)

@datasetRouter.get("/dataset")
async def get_dataset_by_name_req(name: str, db: Session = Depends(get_session)):
  dataset = Dataset.get_by_name(name, db)
  if not dataset: raise HTTPException(status_code=404, detail="Dataset is not found!")
  return dataset.to_response()

@datasetRouter.delete("/datasets/filter")
async def clean_task_type_req(task_type:str,db:Session = Depends(get_session)):
  datasets = Dataset.get_by_task_type(task_type,db)
  dataset.clean_all_datasets(datasets,db)
  return {"msg":"success!"}

@datasetRouter.post(f"/dataset",response_model=DatasetResponseSchema)
async def post_dataset_req(background_task:BackgroundTasks,payload: DatasetRequestSchema,db:Session = Depends(get_session)):
  try:
    tt = payload.tt()
    q = create_dummy(payload) if tt.is_dummies() else dataset.create_dataset(payload)
    q.save(db)
    if not tt.is_dummies(): background_task.add_task(pulling,dataset_name=q.name)
    return q.to_response()
  except Exception as e: raise HTTPException(status_code=500,detail=str(e))

@datasetRouter.get("/dataset/sample")
async def get_sample_req(name: str, db: Session = Depends(get_session)):
  q = Dataset.get_by_name(name,db)
  return  dataset.get_df_sample(q,10)

@datasetRouter.get("/dataset/describe")
async def get_description_req(name: str, db: Session = Depends(get_session)):
  q = Dataset.get_by_name(name,db)
  return dataset.get_df_describe(q)

@datasetRouter.get("/dataset/pca")
async def get_pca_req(name:str,db:Session = Depends(get_session)):
  q = Dataset.get_by_name(name,db)
  return dataset.dim_reduce(q)

@datasetRouter.delete("/dataset")
async def delete_dataset_req(name:str,db:Session=Depends(get_session)):
  return dataset.delete_dataset(name,db)

@datasetRouter.get("/utils/mapping")
async def get_mapping_req(): return dataset.get_mapping()

@datasetRouter.get("/utils/tagname")
async def get_tagname_req(row_id:int): return {"tagname":dataset.get_mapping()[row_id]}



