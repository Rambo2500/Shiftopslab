import sqlite3
conn = sqlite3.connect('data/shiftopspro.db')
for row in conn.execute("SELECT COUNT(*) FROM schedule_assignments WHERE scheduled_date LIKE '2026-03-08%'"):
    print(row)
conn.close()
