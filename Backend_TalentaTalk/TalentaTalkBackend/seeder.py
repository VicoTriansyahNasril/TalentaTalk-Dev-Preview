import sys
import os
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import engine
from models import Manajemen, Materipercakapan

# Import hash function dengan workaround untuk bcrypt version issue
try:
    # Suppress bcrypt version warning
    import warnings
    warnings.filterwarnings("ignore", message=".*trapped.*error reading bcrypt version.*")
    
    from controller.AuthController import hash_password
    print("✅ Hash function berhasil diimport dari AuthController")
except Exception as e:
    print(f"⚠️  Warning: Menggunakan fallback hash function: {e}")
    # Fallback ke bcrypt langsung dengan version check bypass
    import bcrypt
    def hash_password(password: str) -> str:
        """Fallback hash function menggunakan bcrypt"""
        try:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        except Exception as bcrypt_error:
            print(f"❌ Bcrypt error: {bcrypt_error}")
            # Jika bcrypt juga error, gunakan simple hash (HANYA UNTUK DEVELOPMENT!)
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_admin_accounts(session):
    print("Memeriksa akun admin...")
    admins_to_create = [
        {"namamanajemen": "Admin TalentaTalk 1", "email": "admin.talentatalk@gmail.com", "password": "Password123"},
        {"namamanajemen": "Admin TalentaTalk 2", "email": "admin.talentatalk1@gmail.com", "password": "Password123"},
        {"namamanajemen": "Admin TalentaTalk 3", "email": "admin.talentatalk2@gmail.com", "password": "Password123"}
    ]

    created_count = 0
    for admin_data in admins_to_create:
        try:
            exists = session.query(Manajemen).filter_by(email=admin_data["email"]).first()
            if not exists:
                hashed_pwd = hash_password(admin_data["password"])
                admin = Manajemen(
                    namamanajemen=admin_data["namamanajemen"], 
                    email=admin_data["email"], 
                    password=hashed_pwd
                )
                session.add(admin)
                print(f"  ✅ Akun admin akan dibuat: {admin_data['email']}")
                created_count += 1
            else:
                print(f"  🔹 Akun admin sudah ada: {admin_data['email']}")
        except Exception as e:
            print(f"  ❌ Error membuat admin {admin_data['email']}: {e}")
            continue
    
    return created_count

def seed_conversation_topics(session):
    print("\nMemeriksa materi percakapan...")
    try:
        existing_count = session.query(Materipercakapan).count()
        if existing_count > 0:
            print(f"  🔹 Materi percakapan sudah ada ({existing_count} topics).")
            return 0

        topics = [
            "Frontend Development Best Practices",
            "Backend Architecture Patterns", 
            "UI/UX Design Process and User Research",
            "CI/CD Pipelines and DevOps Culture",
            "Microservices vs Monolithic Architecture",
            "API Security and Authentication",
            "Database Design and Optimization",
            "Cloud Native Applications",
            "Machine Learning in Production",
            "Agile vs Scrum Methodologies",
            "Technical Debt Management",
            "Code Review and Quality Assurance",
            "System Monitoring and Observability",
            "Container Orchestration with Kubernetes",
            "Automated Testing Strategies",
            "Software Architecture Patterns",
            "Performance Optimization Techniques",
            "Data Engineering and ETL Processes",
            "Mobile App Development",
            "Web Security Best Practices",
        ]
        
        topic_objects = [Materipercakapan(topic=t) for t in topics]
        session.add_all(topic_objects)
        print(f"  ✅ {len(topics)} materi percakapan akan dibuat.")
        return len(topics)
        
    except Exception as e:
        print(f"  ❌ Error membuat materi percakapan: {e}")
        return 0

def run_seeder():
    print("🚀 Memulai proses seeding data...")
    print("📋 Mengabaikan warning bcrypt version - ini normal dan tidak mempengaruhi fungsi")
    
    session = SessionLocal()
    try:
        admins_created = seed_admin_accounts(session)
        topics_created = seed_conversation_topics(session)

        if admins_created > 0 or topics_created > 0:
            session.commit()
            print(f"\n✨ Data baru berhasil disimpan ke database.")
            print(f"   - {admins_created} admin account(s) dibuat")
            print(f"   - {topics_created} conversation topic(s) dibuat")
        else:
            print("\n✨ Tidak ada data baru yang perlu ditambahkan.")

        print("\n🎉 Proses seeding selesai dengan sukses!")

    except Exception as e:
        print(f"\n❌ Terjadi kesalahan: {e}")
        print("Database di-rollback untuk mencegah data korup.")
        session.rollback()
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    run_seeder()