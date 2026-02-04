import asyncio
import logging
from passlib.context import CryptContext
from sqlalchemy import select, delete
from app.core.database import AsyncSessionLocal, engine, Base
from app.models.models import Manajemen

# Logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Data Admin Default
ADMIN_DATA = [
    {
        "namamanajemen": "Admin",
        "email": "admin@gmail.com",
        "password": "admin123"
    }
]

async def seed_admins():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Manajemen).where(Manajemen.email == ADMIN_DATA[0]["email"]))
            existing_admin = result.scalar_one_or_none()

            if not existing_admin:
                logger.info("🌱 Seeding Admin Baru...")
                new_admin = Manajemen(
                    namamanajemen=ADMIN_DATA[0]["namamanajemen"],
                    email=ADMIN_DATA[0]["email"],
                    password=get_password_hash(ADMIN_DATA[0]["password"])
                )
                session.add(new_admin)
                await session.commit()
                logger.info("✅ Admin berhasil dibuat: admin@gmail.com / admin123")
            else:
                logger.info("🔄 Admin ditemukan, mereset password ke default...")
                existing_admin.password = get_password_hash(ADMIN_DATA[0]["password"])
                await session.commit()
                logger.info("✅ Password Admin di-reset: admin123")

        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Seeder Error: {e}")
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(seed_admins())