import pandas as pd,numpy as np
from app.database.schemas import SupervisedResponseSchema,TaskType,StatusProcess,InferenceRequestSchema
from app.database.orm import Dataset,ModelML
from app.database.db import get_session
from fastapi import HTTPException



class Supervised():
  @staticmethod
  def inference(payload:InferenceRequestSchema,db=None):pass

  @staticmethod
  def auto_inference():pass

  @staticmethod
  def finetune():pass

  @staticmethod
  def find_top_model():pass

  @staticmethod
  def train():pass

