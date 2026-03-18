import sqlite3
conn = sqlite3.connect('data/shiftopspro.db')
for row in conn.execute("SELECT team, COUNT(*) FROM employees WHERE active=1 AND is_schedulable=1 GROUP BY team"):
    print(row)
conn.close()
