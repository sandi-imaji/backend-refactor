import pandas as pd,numpy as np,random,uuid,datetime
from fastapi import HTTPException
from pycaret.datasets import get_data
from app.config import Config
from app.helpers import init_storages_dataset
from app.database.schemas import TaskType,DatasetRequestSchema,StatusProcess,MetaDataset
from app.database.orm import Dataset


INDEX_DATASET_DUMMY : dict = {
  "Classification" : ["boston","bike","concrete","diamond","energy"],
  "Regression" : ["glass","iris","poker","questions","satellite"],
  "Clustering" : ["facebook","ipl","jewellery","migration","perfume"],
  "Anomaly" : ["anomaly"],
  "TimeSeries": []
}

def generate_dataset_dummy(idx): return get_data(idx,verbose=False)

def create_dummy(payload:DatasetRequestSchema) -> Dataset:
  all_index = get_data("index",verbose=False)
  idx_rnd = random.choice(INDEX_DATASET_DUMMY[payload.tt().base])
  df = get_data(idx_rnd,verbose=False)
  columns = df.columns.tolist()
  name = f"{payload.task_type}-{str(uuid.uuid4())[:8]}"
  payload.description += f" {idx_rnd}"
  init_storages_dataset(name)
  if payload.tt().is_supervised():
    target = all_index[all_index["Dataset"] == idx_rnd]["Target Variable 1"].item()
    features = [col for col in columns if col != target]
    payload.target = target
  else: features = columns
  path = f"storages/{name}/data.csv"
  df.to_csv(Config.dir/path,index=False)
  n_rows,n_cols = df.shape
  meta = MetaDataset(
    created_at = datetime.datetime.now().isoformat(),
    created_by = "Anonymous",
    size_of = df.memory_usage().sum(),
    n_rows = n_rows,
    n_cols = n_cols,
    missing_values=df.isna().sum().sum().item(),
    is_outlier = False, random_seed = 4,
    columns = df.columns.tolist(),notes = "", train_size = 0.8,
    path = path
  ).model_dump()
 
  payload.features = features
  return Dataset(
    name = name,
    is_valid = False,
    status = StatusProcess.SUCCESS_PULL,
    meta = meta,
    **payload.model_dump()
  )

if __name__ == "__main__":pass
