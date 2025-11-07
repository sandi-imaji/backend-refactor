from datetime import datetime
from app.config import Config
import os

FMT_DT = "%Y%m%d"

def encode_to_dt_sl(timestamps): return datetime.strptime(timestamps, "%Y%m%d").strftime("%d %b %Y")

def decode_date_unix(unix_timestamps):pass

def encode_date_unix(timestamps):pass

def init_storages_dataset(name):
  path = Config.dir/"storages"/name
  os.makedirs(path,exist_ok=True)
  os.makedirs(path/"logs",exist_ok=True)
  os.makedirs(path/"top_model",exist_ok=True)
  print("Init Storages ...")


if __name__ == "__main__":
  print(Config.dir_app)
  print(Config.dir)

