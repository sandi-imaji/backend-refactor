import logging
from sqlmodel import SQLModel, create_engine, Session

from app.database.orm import Dataset,ModelML
# Gunakan path absolut yang lebih aman
DATABASE_URL = "sqlite:///./storages/rtdb/data.db"

# Buat engine global
engine = create_engine(DATABASE_URL, echo=False)

# Konfigurasi logging untuk SQLAlchemy
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_session():
  """Dependency untuk mendapatkan session database."""
  with Session(engine) as session: yield session


def init_db(drop_existing: bool = False):
  """Inisialisasi database: membuat tabel sesuai model SQLModel."""
  print("Inisialisasi database...")

  if drop_existing:
    print("Menghapus tabel lama...")
    SQLModel.metadata.drop_all(engine)

  print("Membuat tabel baru (jika belum ada)...")
  SQLModel.metadata.create_all(engine)

  print("Tabel selesai dibuat.")


if __name__ == "__main__":
  init_db()

