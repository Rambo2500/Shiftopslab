import sqlite3
conn = sqlite3.connect('data/shiftopspro.db')
query = """
SELECT e.team, s.name, COUNT(*) 
FROM schedule_assignments sa 
JOIN employees e ON sa.employee_id = e.id 
JOIN shifts s ON sa.shift_id = s.id 
WHERE sa.scheduled_date LIKE '2026-03-08%' 
GROUP BY e.team, s.name
"""
for row in conn.execute(query):
    print(row)
conn.close()
