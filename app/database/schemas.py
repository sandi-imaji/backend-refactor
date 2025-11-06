from pydantic import BaseModel
from typing import Any,Optional,List,Union,Dict
from enum import Enum,auto
from pandas import read_csv


class StatusProcess(Enum):
  PENDING = auto()         # Menunggu proses dimulai
  RUNNING_PULL = auto()    # Sedang jalan
  SUCCESS_PULL = auto()    # Tugas Selesai dengan sukses
  ERROR_PULL = auto()      # Ada masalah atau kegagalan
  RUNNING_TRAIN = auto()
  SUCCESS_TRAIN = auto()
  ERROR_TRAIN = auto()
  RUNNING_COMPARE = auto()
  IDLE = auto()
  ACTIVE = auto()
  PAUSED = auto()     # Proses dihentikan
  CANCELLED = auto()  # Proses dibatalkan
  QUEUED = auto()     # Menunggu antrian
  VALIDATING = auto() # Memeriksa data / model

  def __str__(self): return self.name

class TaskType(Enum):
  Classification = auto()
  Regression = auto()
  Clustering = auto()
  TimeSeries = auto()
  Anomaly = auto()
  ClassificationDummy = auto()
  RegressionDummy = auto()
  ClusteringDummy = auto()
  TimeSeriesDummy = auto()
  AnomalyDummy = auto()

  @classmethod
  def tolist(cls): return list(cls.__members__.keys())
  def is_classification(self): return self in [TaskType.Classification,TaskType.ClassificationDummy]
  def is_regression(self): return self in [TaskType.Regression,TaskType.RegressionDummy]
  def is_clustering(self): return self in [TaskType.Clustering,TaskType.ClusteringDummy]
  def is_anomaly(self): return self in [TaskType.Anomaly,TaskType.AnomalyDummy]
  def is_timeseries(self): return self in [TaskType.TimeSeries,TaskType.TimeSeriesDummy]

  def is_supervised(self): return self.is_classification() or self.is_regression()
  def is_unsupervised(self): return self.is_clustering() or self.is_anomaly()
  def is_dummies(self): return self in [TaskType.ClassificationDummy,TaskType.RegressionDummy,TaskType.TimeSeriesDummy.AnomalyDummy,TaskType.ClusteringDummy]

  @staticmethod
  def from_str(task_type:str): return eval(f"TaskType.{task_type}")

  def module(self):
    if self.is_classification():
      from pycaret import classification
      return classification
    elif self.is_regression():
      from pycaret import regression
      return regression
    elif self.is_clustering():
      from pycaret import clustering
      return clustering
    elif self.is_timeseries():
      from pycaret import time_series
      return time_series
    elif self.is_anomaly():
      from pycaret import anomaly
      return anomaly
    else: raise TypeError("Task Type invalid !")

  def algorithms(self):
    import json,os
    filepath = "./algorithm_list.json"
    if not os.path.exists(filepath): raise ValueError(f"{filepath} is not found!")
    with open(filepath,"r") as f :
      data = json.load(f)
      assert self.name in data.keys(),f"{self.name} not in algorithms : {data.keys()}"
      return data[self.name]
  
  def __str__(self): return self.name



class MetaDataset(BaseModel):
  created_by:str
  created_at:str
  size_of:int
  n_rows:int
  n_cols:int
  notes:Optional[str]
  train_size:float
  missing_values:int
  is_outlier:Optional[bool]
  random_seed:Optional[int]
  columns:List[Any]
  path:str

class DatasetRequestSchema(BaseModel):
  description:str = ""
  task_type:str
  features:List[str]
  target:Union[str,int]
  start_date:str
  end_date:str
  time_start:str = "00:00:00"
  time_end:str = "23:59:00"
  interval:int = 0

class PreprocessingSchema(BaseModel):
  missing_values:dict
  scaling:dict
  transformation:dict
  outlier_handling:dict
  dimensionality_reduction:dict
  cv:dict

class DatasetResponseSchema(BaseModel):
  task_type:str
  description:str
  names:str
  features:List[str]
  target:Union[str,int]
  start_date:str
  end_date:str
  interval:int
  is_valid:bool
  meta:Optional[MetaDataset] = None
  preprocessing:Optional[PreprocessingSchema] = None
  top_model:Optional[str] = None
  models:List[Any] = []
  status:str

class ModelResponseSchema(BaseModel):
  name:str
  dataset_name:str
  algorithm:str
  is_active:bool
  finetune:bool
  evaluation:dict
  meta:Optional[dict]
  status:str

class MetaModel(BaseModel):
  created_by:str
  created_at:str
  size_of:int
  notes:str

class ViewModels(BaseModel):
  name:str
  evaluation:Dict
  algorithm:str
  description:str
  path:str


