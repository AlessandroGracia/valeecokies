import sqlite3

conn = sqlite3.connect('galletas.db')
cursor = conn.cursor()

# Fix cajas_diarias UTC offset
cursor.execute("UPDATE cajas_diarias SET opened_at = datetime(opened_at, '-5 hours') WHERE opened_at > '2026-04-14 00:00:00'")
cursor.execute("UPDATE cajas_diarias SET closed_at = datetime(closed_at, '-5 hours') WHERE closed_at > '2026-04-14 00:00:00' AND closed_at IS NOT NULL")
cursor.execute("UPDATE cajas_diarias SET date = date(datetime(date, '-5 hours')) WHERE date > '2026-04-14'")

conn.commit()
print(f"Updated {cursor.rowcount} entries in cajas_diarias")
conn.close()
