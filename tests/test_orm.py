from app.database.orm import Dataset,ModelML
from app.database.schemas import StatusProcess,TaskType
from app.database.db import get_session
import unittest,json,uuid


def create_clustering()-> Dataset:
  features = ['216946529', '216948739', '216946530']
  target = "2"
  task_type = TaskType.Clustering
  description = "Test Clustering"
  name = f"{task_type}-{str(uuid.uuid4())[:8]}"
  start_time = "00:00:00"
  end_time = "23:59:00"
  start_date =  "20250827"
  end_date = "20250927"
  
  data =  Dataset(task_type=task_type,
              features=features,
              target=target,
              name=name,
              status = StatusProcess.IDLE,
              description=description,
              interval=5,
              is_valid=True,
              time_start = start_time,
              time_end = end_date,
              start_date = start_date,
              end_date = end_date,
              meta = 
              )


class TestDataset(unittest.TestCase):
  def setUp(self) -> None:
    db = next(get_session())
    with open("tests/dataset_samples.json","r") as f:
      data = json.load(f)
    for d in data:
      print(d["status"])

  def test_create(self):
    target = "20"
    data = Dataset(task_type=TaskType.Classification,
                   features= features,
                   target = target,
                   name = ""

                   )


if __name__ == "__main__":
  unittest.main()






