# reset_db.py

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Menambahkan root direktori ke path agar bisa import module lain
# Sesuaikan '..' jika struktur direktori Anda berbeda
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import engine, DATABASE_URL
from models import Base

def reset_database():
    """
    Menghapus semua tabel dari database dan membuatnya kembali.
    PERINGATAN: SEMUA DATA AKAN HILANG!
    """
    print("="*50)
    print("PERINGATAN: Operasi ini akan menghapus SEMUA data di database.")
    print(f"Target Database: {DATABASE_URL}")
    print("="*50)
    
    confirm = input("Apakah Anda yakin ingin melanjutkan? (ketik 'yes' untuk konfirmasi): ")
    
    if confirm.lower() != 'yes':
        print("Operasi dibatalkan.")
        return

    print("\nMenghapus tabel lama...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("✅ Tabel lama berhasil dihapus.")
    except Exception as e:
        print(f"❌ Error saat menghapus tabel: {e}")
        return

    print("Membuat tabel baru...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tabel baru berhasil dibuat.")
        print("\nDatabase berhasil di-reset ke kondisi awal!")
    except Exception as e:
        print(f"❌ Error saat membuat tabel: {e}")

if __name__ == "__main__":
    reset_database()