import os,pathlib
from datetime import timedelta,timezone
from dataclasses import dataclass

DELAY = int(os.environ.get("DELAY",0))
WORKER = False if str(os.environ.get("WORKER") == "0") else True

@dataclass
class Config:
  dir_app = pathlib.Path(__file__).parent
  dir = pathlib.Path(__file__).parent.parent
  url   :str = "https://10.3.13.1/beta2/application/api"
  token :str = "8bcd07bfd39cee93071bd10ed3ac1234"
  key   :str = "f029c429282463ae3088bd25e9e4be72"
  verbose = bool(os.environ.get("VERBOSE",False))
  utc = timezone(timedelta(hours=7))

COLOR_MAP : dict = {
    "DEBUG": "\033[36m",    # Cyan
    "INFO": "\033[32m",     # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",    # Red
    "CRITICAL": "\033[41m", # Red background
    "RESET": "\033[0m",
}
