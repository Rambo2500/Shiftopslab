from workforce_engine.database import SessionLocal
from workforce_engine.models import Shift

db = SessionLocal()
try:
    print("--- SHIFT TABLE CONTENT ---")
    shifts = db.query(Shift).all()
    for s in shifts:
        print(f"Name: '{s.name}', Start: {s.start_hour}:{s.start_minute:02d}, Duration: {s.duration_minutes}m")
finally:
    db.close()
