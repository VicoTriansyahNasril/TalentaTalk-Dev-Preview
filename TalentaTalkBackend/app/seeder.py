import asyncio
import logging
from passlib.context import CryptContext
from sqlalchemy import select
# Import engine dan Base untuk pembuatan tabel otomatis
from app.core.database import AsyncSessionLocal, engine, Base
from app.models.models import Manajemen

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigurasi Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Data Admin Awal
ADMIN_DATA = [
    {
        "namamanajemen": "Super Admin",
        "email": "admin@talentatalk.com",
        "password": "password123"
    },
    {
        "namamanajemen": "Manager Content",
        "email": "content@talentatalk.com",
        "password": "password123"
    }
]

async def init_tables():
    """
    Fungsi krusial: Membuat tabel di database jika belum ada
    berdasarkan definisi di models.py
    """
    logger.info("🛠️  Memeriksa dan membuat tabel database...")
    async with engine.begin() as conn:
        # Menjalankan perintah create table secara sinkronus di dalam engine async
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Tabel berhasil diinisialisasi.")

async def seed_admins():
    """
    Fungsi utama seeder.
    """
    # 1. Buat tabel terlebih dahulu sebelum insert data
    await init_tables()

    logger.info("🌱 Memulai proses seeding data Admin (Manajemen)...")
    
    async with AsyncSessionLocal() as session:
        try:
            for data in ADMIN_DATA:
                # 2. Cek apakah email sudah ada
                query = select(Manajemen).where(Manajemen.email == data["email"])
                result = await session.execute(query)
                existing_admin = result.scalar_one_or_none()

                if existing_admin:
                    logger.warning(f"⚠️  Admin dengan email '{data['email']}' sudah ada. Skip.")
                    continue

                # 3. Hash Password
                hashed_password = get_password_hash(data["password"])

                # 4. Buat Object Manajemen
                new_admin = Manajemen(
                    namamanajemen=data["namamanajemen"],
                    email=data["email"],
                    password=hashed_password
                )

                # 5. Tambahkan ke session
                session.add(new_admin)
                logger.info(f"✅ Menambahkan Admin: {data['email']}")

            # 6. Commit perubahan
            await session.commit()
            logger.info("🎉 Proses seeding selesai!")

        except Exception as e:
            logger.error(f"❌ Terjadi kesalahan saat seeding: {e}")
            await session.rollback()
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(seed_admins())