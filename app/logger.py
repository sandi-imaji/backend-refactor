import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.config import COLOR_MAP
from app.config import Config

# Contoh DIR, sesuaikan
DIR = Path(".")

class ColoredFormatter(logging.Formatter):
  def format(self, record):
    color = COLOR_MAP.get(record.levelname, "")
    reset = COLOR_MAP["RESET"]
    message = super().format(record)
    return f"{color}{message}{reset}"

def Logger(dataset_name: str) -> logging.Logger:
  """
  Mengembalikan logger unik untuk tiap dataset_name.
  Jika VERBOSE=1 → tampil juga di terminal (berwarna).
  Jika tidak, hanya menulis ke file.
  """
  if dataset_name == "": log_dir = DIR / "logger"
  else: log_dir = DIR / "storages" / dataset_name / "logs"
  log_dir.mkdir(parents=True, exist_ok=True)

  log_path = log_dir / "main.log"
  logger_name = f"logger_{dataset_name}"
  logger = logging.getLogger(logger_name)
  logger.setLevel(logging.INFO)

  # Hapus handler lama agar tidak duplikat
  if logger.hasHandlers(): logger.handlers.clear()

  # === File handler ===
  file_handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=3)
  file_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
  file_handler.setFormatter(file_formatter)
  logger.addHandler(file_handler)

  # === Tambahkan console handler jika VERBOSE=1 ===
  if Config.verbose:
    console_handler = logging.StreamHandler()
    console_formatter = ColoredFormatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

  return logger
