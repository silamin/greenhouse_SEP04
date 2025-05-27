from api_service.adapters.models import SensorDB, SettingsDB, LoginDB, Base
from api_service.db import SessionLocal, engine
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import random
import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


# Create tables
Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    print("Seeding database...")

    # Insert default settings if not present
    if not db.query(SettingsDB).filter_by(owner="admin").first():
        db.add(SettingsDB(
            owner="admin",
            name="Main Greenhouse",
            temp_min=18,
            temp_max=28,
            light_min=300,
            light_max=1000,
            hum_min=40,
            hum_max=70,
            soil_min=500
        ))

    # Ensure admin user exists and is reset
    admin = db.query(LoginDB).filter_by(username="admin").first()
    if not admin:
        db.add(LoginDB(
            username="admin",
            password_hash=hash_password("admin"),
            is_first_login=True
        ))
    else:
        admin.password_hash = hash_password("admin")
        admin.is_first_login = True
        print("🔁 Admin user exists, resetting password and first login flag.")

    # Add dummy sensor data
    now = datetime.utcnow()
    for i in range(40):
        db.add(SensorDB(
            timestamp=now - timedelta(hours=i * 6),
            temp=round(random.uniform(17, 32), 1),
            hum=round(random.uniform(30, 80), 1),
            soil=random.randint(400, 800),
            light=random.randint(100, 1200),
            dist=random.randint(5, 30),
            motion=bool(random.getrandbits(1)),
            acc_x=random.randint(-100, 100),
            acc_y=random.randint(-100, 100),
            acc_z=random.randint(-100, 100),
        ))

    db.commit()
    print("✅ Seeding complete.")

except IntegrityError as e:
    db.rollback()
    print("❌ Seeding failed due to integrity error.")
    print("Error:", e)

finally:
    db.close()
