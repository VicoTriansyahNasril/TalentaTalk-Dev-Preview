import asyncio
import logging
from passlib.context import CryptContext
from sqlalchemy import delete
from app.core.database import AsyncSessionLocal, engine, Base
from app.models.models import Manajemen

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Data Admin
ADMIN_DATA = [
    {
        "namamanajemen": "Admin",
        "email": "admin@gmail.com",
        "password": "admin123"
    }
]

async def init_tables():
    logger.info("🛠️  Memeriksa dan membuat tabel database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Tabel siap.")

async def seed_admins():
    await init_tables()
    logger.info("🌱 Memulai clean seeding data Admin...")

    async with AsyncSessionLocal() as session:
        try:
            # 1. HAPUS SEMUA DATA LAMA
            logger.warning("🧹 Menghapus seluruh data Manajemen...")
            await session.execute(delete(Manajemen))
            await session.commit()

            # 2. INSERT DATA BARU
            for data in ADMIN_DATA:
                admin = Manajemen(
                    namamanajemen=data["namamanajemen"],
                    email=data["email"],
                    password=get_password_hash(data["password"])
                )
                session.add(admin)

            await session.commit()
            logger.info("🎉 Clean seeding Admin berhasil!")

        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Seeder gagal: {e}")
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(seed_admins())