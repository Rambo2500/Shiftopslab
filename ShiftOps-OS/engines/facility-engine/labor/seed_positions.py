from workforce_engine.database import SessionLocal
from workforce_engine.models import (
    Site, Line, Position, PositionType, Employee, Shift, 
    ScheduleParam, ScheduleAssignment, ConflictLog, RiskLog, RoleType
)

def seed_positions():
    db = SessionLocal()
    site = db.query(Site).filter(Site.name.like("%Elkhart%")).first()
    if not site:
        site = Site(name="Elkhart")
        db.add(site)
        db.commit()
        db.refresh(site)
    
    site_id = site.id
    
    try:
        db.query(ConflictLog).delete()
        db.query(RiskLog).delete()
        db.query(ScheduleAssignment).delete()
        db.query(Position).delete()
        db.query(Line).delete()
        db.query(Shift).delete()
        db.query(ScheduleParam).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error clearing data: {e}")
        return

    # --- SHIFTS ---
    # Full Shifts
    db.add(Shift(site_id=site_id, name="Shipping Day Full", start_hour=5, start_minute=30, duration_minutes=750)) 
    db.add(Shift(site_id=site_id, name="Shipping Night Full", start_hour=17, start_minute=30, duration_minutes=750))
    
    # Wednesday Split Shifts (6.5 hours = 390 min)
    db.add(Shift(site_id=site_id, name="Shipping Wed AM Split", start_hour=5, start_minute=30, duration_minutes=390))
    db.add(Shift(site_id=site_id, name="Shipping Wed PM Split", start_hour=11, start_minute=30, duration_minutes=390))
    
    # Wednesday Night Split Shifts
    db.add(Shift(site_id=site_id, name="Shipping Wed Night Early", start_hour=17, start_minute=30, duration_minutes=390))
    db.add(Shift(site_id=site_id, name="Shipping Wed Night Late", start_hour=23, start_minute=30, duration_minutes=390))

    # Packing Shifts (8.5 hours = 510 min)
    db.add(Shift(site_id=site_id, name="Packer P1", start_hour=7, start_minute=0, duration_minutes=510))
    db.add(Shift(site_id=site_id, name="Packer P2", start_hour=15, start_minute=0, duration_minutes=510))
    db.add(Shift(site_id=site_id, name="Packer P3", start_hour=23, start_minute=0, duration_minutes=510))

    # --- SCHEDULE PARAMS ---
    for d in range(7):
        # Packing: 12 on weekends, 14 on weekdays
        db.add(ScheduleParam(department="Packing", day_of_week=d, required_headcount=14 if 1 <= d <= 5 else 12))
        db.add(ScheduleParam(department="Shipping", day_of_week=d, required_headcount=18))

    # --- PACKING POSITIONS ---
    packing_config = [
        ("Bread", PositionType.BREAD_BUN_ANCHOR, 2, True),
        ("Bun", PositionType.BREAD_BUN_ANCHOR, 2, True),
        ("Muffin Line 1", PositionType.MUFFIN_ANCHOR, 3, True),
        ("Muffin Line 2", PositionType.MUFFIN_ANCHOR, 3, True),
        ("Break Relief", PositionType.BREAK_RELIEF, 2, True),
        ("Floating Position", PositionType.FLOATING, 2, False),
    ]

    for line_name, pos_type, count, weekend_active in packing_config:
        line = Line(name=line_name, site_id=site_id, department="Packing")
        db.add(line)
        db.flush()
        for i in range(1, count + 1):
            db.add(Position(
                site_id=site_id, line_id=line.id, department="Packing",
                position_label=f"{line_name} {i}", position_type=pos_type,
                required_role_type=RoleType.GENERAL,
                is_weekend_active=weekend_active, is_critical=(i==1)
            ))

    # --- SHIPPING POSITIONS (The Core 18) ---
    shipping_line = Line(name="Shipping Dock", site_id=site_id, department="Shipping")
    db.add(shipping_line)
    db.flush()

    shipping_positions = [
        ("Supervisor", PositionType.SHIPPING_FIXED, RoleType.SUPERVISOR, True, 1),
        ("Logistics", PositionType.SHIPPING_FIXED, RoleType.LOGISTICS, True, 1),
        ("Line Lead", PositionType.SHIPPING_FIXED, RoleType.LINE_LEAD, True, 1),
        ("SR Dock", PositionType.SHIPPING_FIXED, RoleType.SR_DOCK, True, 1),
        ("Bread", PositionType.SHIPPING_ROTATIONAL, RoleType.GENERAL, False, 2),
        ("Bun", PositionType.SHIPPING_ROTATIONAL, RoleType.GENERAL, False, 2),
        ("Muffin Line 1", PositionType.SHIPPING_ROTATIONAL, RoleType.GENERAL, False, 1),
        ("Muffin Line 2", PositionType.SHIPPING_ROTATIONAL, RoleType.GENERAL, False, 1),
        ("De-Nester", PositionType.SHIPPING_ROTATIONAL, RoleType.GENERAL, False, 2),
        ("Dock", PositionType.SHIPPING_DOCK, RoleType.GENERAL, False, 2),
        ("Break Relief", PositionType.SHIPPING_ROTATIONAL, RoleType.GENERAL, False, 2),
        ("Floating Position", PositionType.SHIPPING_ROTATIONAL, RoleType.GENERAL, False, 2),
    ]

    for label, p_type, role_enum, critical, count in shipping_positions:
        for i in range(1, count + 1):
            db.add(Position(
                site_id=site_id, line_id=shipping_line.id, department="Shipping",
                position_label=f"{label} {i}" if count > 1 else label, 
                position_type=p_type, required_role_type=role_enum,
                is_critical=critical, is_weekend_active=True
            ))

    db.commit()
    db.close()
    print("Positions re-seeded to match exact spreadsheet requirements.")

if __name__ == "__main__":
    seed_positions()
