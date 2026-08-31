import sqlite3

DATABASE_PATH = "data/database/ecommerce.db"

connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
""")

tables = cursor.fetchall()

print("TABELAS ENCONTRADAS:")
print(tables)

connection.close()

