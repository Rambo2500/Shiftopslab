import sqlite3
conn = sqlite3.connect('data/shiftopspro.db')
for row in conn.execute("SELECT position_label, position_type FROM positions WHERE department='Shipping'"):
    print(row)
conn.close()
