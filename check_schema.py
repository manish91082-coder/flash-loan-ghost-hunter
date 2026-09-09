import sqlite3
db_path = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\phantomx_knowledge.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
for table in tables:
    print(f'Table: {table[0]}')
    print(f'{table[1]}\n')
