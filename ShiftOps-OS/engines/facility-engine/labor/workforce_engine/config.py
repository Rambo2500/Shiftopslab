import os

class ExperienceSettings:
    # Days before an employee is considered a "Veteran"
    EXPERIENCE_THRESHOLD_DAYS = int(os.getenv("EXPERIENCE_THRESHOLD_DAYS", 90))
    
    # Concentration risk levels (Percentages)
    YELLOW_RISK_THRESHOLD = float(os.getenv("YELLOW_RISK_THRESHOLD", 0.20)) # 20%
    RED_RISK_THRESHOLD = float(os.getenv("RED_RISK_THRESHOLD", 0.40))    # 40%

settings = ExperienceSettings()
