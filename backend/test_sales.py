import sqlite3

conn = sqlite3.connect('galletas.db')
cursor = conn.cursor()

# Get the last open cash register
cursor.execute("SELECT id, opened_at, status FROM cajas_diarias ORDER BY id DESC LIMIT 1")
row = cursor.fetchone()
print("Cash Register:", row)

cash_reg_dt = row[1]

cursor.execute("SELECT id, total, sale_date FROM ventas WHERE status='COMPLETADA' AND sale_date >= ?", (cash_reg_dt,))
print("Sales after opened_at:", cursor.fetchall())
conn.close()
