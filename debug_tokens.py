import sqlite3
db_path = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\phantomx_knowledge.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT symbol, contract_address FROM tokens LIMIT 10")
print("Sample tokens:")
for row in c.fetchall():
    print(row)
