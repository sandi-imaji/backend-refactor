from scipy.stats import f
from app.database.orm import Dataset,ModelML
from app.database.schemas import StatusProcess,TaskType
from app.database.db import get_session
import unittest,json,uuid,requests as req,json


def create_clustering():
  features = ['216946529', '216948739', '216946530']
  target = "2"
  task_type = TaskType.Clustering
  description = "Test Clustering"
  name = f"{task_type}-{str(uuid.uuid4())[:8]}"
  start_time = "00:00:00"
  end_time = "23:59:00"
  start_date =  "20250827"
  end_date = "20250927"


class TestDatasetDummy(unittest.TestCase):
  def setUp(self) -> None:
    self.list_tt = TaskType.dummies()

  def test_create(self):
    payload = lambda tt : {
    "description" : "Test 123",
    "task_type": str(tt),
    "features": ["216946529","216948739","216946530","216948740"],
    "target": "216946531",
    "start_date": "20250901",
    "end_date": "20250930",
    "time_start": "00:00:00",
    "time_end": "23:59:00",
    "interval":0
    }
    url = "http://127.0.0.1:8001/dataset"
    for tt in self.list_tt:
      if tt == TaskType.TimeSeriesDummy:
        continue
      res = req.post(url,data=json.dumps(payload(tt)))
      if res.status_code == 200:
        resp = res.json()
        print(f"Dataset Dummy : {resp.get('names','Unknown')} successfully")
      else:
        print(f"Dataset ERROR : {res.text}!")



if __name__ == "__main__":
  unittest.main()






