import sqlite3
conn = sqlite3.connect('data/shiftopspro.db')
query = """
SELECT p.position_label, e.last_name, s.name
FROM schedule_assignments sa 
JOIN positions p ON sa.position_id = p.id 
LEFT JOIN employees e ON sa.employee_id = e.id 
JOIN shifts s ON sa.shift_id = s.id
WHERE sa.scheduled_date LIKE '2026-03-08%' 
AND p.department = 'Shipping'
ORDER BY p.position_label
"""
for row in conn.execute(query):
    print(row)
conn.close()
