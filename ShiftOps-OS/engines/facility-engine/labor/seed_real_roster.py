from workforce_engine.database import SessionLocal
from workforce_engine.models import Employee, DepartmentType, EmploymentStatus, RoleType
from datetime import date

def seed_real_roster():
    db = SessionLocal()
    site_id = "d13733ad-45aa-4bf0-8325-cc0951a9be53"
    
    # Clear existing employees for this site to avoid duplicates
    db.query(Employee).filter(Employee.site_id == site_id).delete()

    packing_employees = [
        ("Melvin", "Baltimore", "P1"), ("Samantha", "Bellamy", "P1"), ("Sabrina", "Benaouicha", "P1"),
        ("Amy", "Blosser", "P1"), ("Brenton", "Butler", "P1"), ("Blanca", "Campos", "P1"),
        ("Beatrice", "Flores", "P1"), ("Rickey", "Garrett", "P1"), ("Sandra", "Hernandez Quiroz", "P1"),
        ("Shannon", "Howell", "P1"), ("Steven", "Maltos", "P1"), ("Panida", "Perry", "P1"),
        ("Mary", "Pettit", "P1"), ("Tammy", "Pinnix", "P1"), ("Petrona", "Quintano", "P1"),
        ("Aqua", "Rivera", "P1"), ("Steven", "Todman", "P1"), ("Kathryn", "Yawkey", "P1"),
        
        ("Laurie", "Abrell", "P2"), ("Gage", "Blessing", "P2"), ("Diana", "Bravo Acevedo", "P2"),
        ("Matthew", "Bruno", "P2"), ("Jeffery", "Fraze", "P2"), ("Jessica", "Jimenez Aguirre", "P2"),
        ("Nathan", "Kitchen", "P2"), ("Janet", "Newell", "P2"), ("Yuleysy", "Ortiz", "P2"),
        ("Tara", "Podemski", "P2"), ("Yuraidy", "Rodriguez Velasquez", "P2"), ("Devyn", "Scroggins", "P2"),
        ("Taliyah", "Vazquez-Burgos", "P2"), ("Leqiesha", "Wright", "P2"),

        ("Belinda", "Baughman", "P3"), ("Keniya", "Delgado", "P3"), ("Darla", "Fulford", "P3"),
        ("Amanda", "Garner", "P3"), ("James", "Jenkins", "P3"), ("Lisa", "Longacre", "P3"),
        ("Dawn", "Murphy", "P3"), ("Daphne", "Palmer", "P3"), ("Daniel", "Pinch", "P3"),
        ("Benjamin", "Pujols", "P3"), ("Nancy", "Rico Fisher", "P3"), ("Milishia", "Rufino", "P3"),
        ("Magdalena", "Russell", "P3"), ("Sandra", "Smith", "P3"), ("Bobby Jo", "Stark", "P3"),
        ("Myriam", "Walker", "P3"), ("Terrence", "Williams", "P3")
    ]

    # Shipping Employees with specific Anchor/Fixed flags
    shipping_employees = [
        ("Melissa", "Miller", "A", True), ("Robert", "Astorga", "A", False), ("Shawn", "Cobb", "A", False),
        ("Joel", "Colvin", "A", False), ("Anthony", "Durr", "A", False), ("Histon", "Gondwe", "A", False),
        ("Keandre", "Hill", "A", False), ("Michael", "Hopkins", "A", False), ("Shaina", "Hunter", "A", False),
        ("Brent", "Hyatt", "A", False), ("Michael", "Kentgen", "A", False), ("Creighton", "Minder", "A", False),
        ("Tara", "Mullins", "A", False), ("Drew", "Nagy", "A", False), ("William", "Oakes", "A", False),
        ("Esgardo", "Quintanilla", "A", False), ("Jimmy", "Recinos", "A", False), ("Riri", "Watson", "A", False),

        ("Alvaro", "Rodriguez Murillo", "B", True), ("Trenton", "Beeson", "B", False), ("Emmett", "Bryant", "B", False),
        ("James", "Coleman", "B", False), ("Olivia", "Cox", "B", False), ("Juan", "Delgado", "B", False),
        ("Derick", "Duran", "B", False), ("Hugo", "Hernandez Montes", "B", False), ("Adonis", "Holloway", "B", False),
        ("David", "Hyatt", "B", False), ("Jeffrey", "Kovach", "B", False), ("Alicia", "Lewis", "B", False),
        ("Brian", "Lopez Rodriguez", "B", False), ("Jeffery", "Marbury", "B", False), ("Jeffrey", "McCorquodale", "B", False),
        ("Phillip", "Reid", "B", False), ("Samuel", "Sidwell", "B", False), ("Bryan", "Stice", "B", False),

        ("Laura", "Vivanco", "C", True), ("LaMon", "Anderson", "C", False), ("Nicholas", "Barton", "C", False),
        ("Jose", "Castro Santos", "C", False), ("Cornisha", "Conner", "C", False), ("Arvonti", "Donaldson", "C", False),
        ("D'Arjon", "Donaldson", "C", False), ("Hezekiah", "Garcia", "C", False), ("Alvaro", "Gomez", "C", False),
        ("Aaron", "Johnson", "C", False), ("Josias", "Juarez", "C", False), ("Juan", "Lozada", "C", False),
        ("Anthony", "Messenger", "C", False), ("Oscar", "Ocampo-Perez", "C", False), ("Bruce", "Smith", "C", False),
        ("James", "Wendt", "C", False),

        ("Taylor", "Leonard", "D", True), ("Derek", "Ash", "D", False), ("DaVon", "Baker", "D", False),
        ("Phillip", "Buck", "D", False), ("Marvin", "Calhoun", "D", False), ("Jaheim", "Coleman", "D", False),
        ("Cornelius", "Conner", "D", False), ("Kenjuan", "Delgado", "D", False), ("John", "Dillard", "D", False),
        ("Jaylen", "Griffin", "D", False), ("Dashin", "Kery", "D", False), ("Robert", "Kjergaard", "D", False),
        ("Louis", "Oneal", "D", False), ("Arohi", "Patel", "D", False), ("Nathan", "Riffle", "D", False),
        ("Genaro", "Vazquez", "D", False),
        
        ("Armon", "Hurt", "AB", False)
    ]

    for first, last, team in packing_employees:
        db.add(Employee(
            site_id=site_id, first_name=first, last_name=last, team=team,
            department=DepartmentType.PACKING, active=True,
            employment_status=EmploymentStatus.ACTIVE, role_type=RoleType.GENERAL,
            is_schedulable=True, is_rotating=True, hire_date=date(2023, 1, 1),
            is_fixed_role=False
        ))

    for first, last, team, is_anchor in shipping_employees:
        db.add(Employee(
            site_id=site_id, first_name=first, last_name=last, team=team,
            department=DepartmentType.SHIPPING, active=True,
            employment_status=EmploymentStatus.ACTIVE, role_type=RoleType.GENERAL,
            is_schedulable=True, is_rotating=False, hire_date=date(2023, 1, 1),
            is_fixed_role=is_anchor
        ))

    db.commit()
    print(f"Seeded {len(packing_employees) + len(shipping_employees)} real employees.")
    db.close()

if __name__ == "__main__":
    seed_real_roster()
