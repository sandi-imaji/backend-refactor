from fastapi import HTTPException
from app.database.schemas import DatasetResponseSchema,DatasetRequestSchema, StatusProcess,TaskType
from app.database.orm import Dataset
from app.config import Config
import os,uuid,shutil,pandas as pd
from typing import Optional
from app.helpers import init_storages_dataset

TAGNAME = pd.read_csv("tagname.csv")

def check_integrity_dataset(dataset:Optional[Dataset]):
  if not dataset: raise HTTPException(status_code=404,detail="Dataset is not found!")
  if not dataset.is_valid: raise HTTPException(status_code=500,detail="Dataset is not valid")
  if not dataset.meta: return HTTPException(status_code=404,detail="dataset is haven't meta!")
  path = Config.dir/"storages"/dataset.name
  if not os.path.exists(path): raise HTTPException(status_code=404,detail=f"Path is not found : {path}")
  if not os.path.exists(path/"data.csv"): raise HTTPException(status_code=404,detail="Dataframe is not found!")

def check_create_dataset(payload:DatasetRequestSchema):
  if not isinstance(payload.features,(list,tuple)): raise HTTPException(status_code=404,detail="features should list or tuple")
  if not all(isinstance(x,str) for x in payload.features): raise HTTPException(status_code=404,detail=f"col is'nt str")
  if not isinstance(payload.target,(int,str)): raise HTTPException(status_code=404,detail=f"target is {type(payload.target)} not int or str")
  if len(payload.features) == 0 : raise HTTPException(status_code=404,detail="feature is None")
  columns = payload.features
  if isinstance(payload.task_type,TaskType):
    if payload.task_type.is_supervised():
      if not payload.target: raise HTTPException(status_code=404,detail="target is not found!")
      columns += [payload.target]
    else:
      if not str(payload.target).isdigit(): raise HTTPException(status_code=500,detail ="")

def create_dataset(payload:DatasetRequestSchema):
  check_create_dataset(payload) 
  name = f"{payload.task_type}-{str(uuid.uuid4())[:8]}"
  init_storages_dataset(name)
  return Dataset(
    name = name,
    is_valid = False,
    status = StatusProcess.PENDING,
    **payload.model_dump()
  )

def clean_all_datasets(datasets,db)->dict:
  if not datasets: raise HTTPException(status_code=500,detail="Dataset udah dihapus")
  for d in datasets:
    filepath = Config.dir/"storages"/d.name
    print(filepath)
    if os.path.exists(filepath): shutil.rmtree(filepath)
    db.delete(d)
    db.commit()
  return {"detail":"datasets is removed"}

def delete_dataset(name,db,logger=None):
  if logger:logger.info("Deleting Datasets ...")
  if name == 'ALL-':
    datasets = db.query(Dataset).all()
    if logger:logger.info(f"All Dataset is has been delete")
    return clean_all_datasets(datasets,db)
  dataset = Dataset.get_by_name(name,db)
  if not dataset: raise HTTPException(status_code=404,detail="Dataset is not found!")
  if logger:logger.error("Dataset is not found!")
  dataset_name = dataset.name
  path  = Config.dir/"storages"/dataset.name
  if os.path.exists(path): shutil.rmtree(path)
  db.delete(dataset)
  db.commit()
  if logger:logger.info(f"Dataset is has been delete | dataset_name : {dataset_name}")
  return {"detail":"dataset is has been delete","dataset_name":dataset_name}

def get_df_sample(dataset:Optional[Dataset],n_samples):
  if not dataset: raise HTTPException(status_code=404,detail="Dataset is not found!")
  if not dataset.is_valid: raise HTTPException(status_code=500,detail="Dataset invalid!")
  pathfile = Config.dir/"storages"/dataset.name/"data.csv"
  if not os.path.exists(pathfile): raise ValueError(f"{pathfile} is not found!")
  df = pd.read_csv(pathfile)
  return df.sample(n_samples).to_dict(orient="index")

def get_df_describe(dataset:Optional[Dataset]):
  if not dataset: raise HTTPException(status_code=404,detail="Dataset is not found!")
  if not dataset.is_valid: raise HTTPException(status_code=500,detail="Dataset invalid!")
  pathfile = Config.dir/"storages"/dataset.name/"data.csv"
  if not os.path.exists(pathfile): raise ValueError(f"{pathfile} is not found!")
  return pd.read_csv(pathfile).describe()

def dim_reduce(dataset,n_components=2,to_dict=True):
  from sklearn.preprocessing import StandardScaler
  from sklearn.decomposition import PCA
  if not dataset: return HTTPException(status_code=404,detail="dataset is not found!")
  if not dataset.is_valid: return HTTPException(status_code=404,detail="dataset is not valid!")
  if not dataset.meta: return HTTPException(status_code=404,detail="dataset is haven't meta!")
  cols = dataset.features
  path = Config.dir/dataset.meta['path']/"data.csv"
  X = pd.read_csv(path)[cols].values
  X_scaled = StandardScaler().fit_transform(X)
  assert len(cols) > 1 ,cols 
  if len(cols) == 2: df = pd.DataFrame(X_scaled,columns=cols)
  else: df = pd.DataFrame(PCA(n_components=n_components).fit_transform(X_scaled),columns=["X1","X2"])
  return df.to_dict(orient="index") if to_dict else df

def get_mapping():
  data = {}
  for _,v in TAGNAME.iterrows(): data[v['row_id']] = v.to_dict()
  return data

def get_tagname(row_id:int): return {"tagname":get_mapping().get(row_id,"")}



