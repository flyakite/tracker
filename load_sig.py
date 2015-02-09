import sqlite3
import re
import json
conn = sqlite3.connect('signal')
c = conn.cursor()
c.execute('select * from result')
rows = c.fetchall()

names = []
with open('emails', 'w') as f:
  for r in rows:
    k, v, u = r
    for m in re.finditer(r'\{\"([^@^"]+?@[^"]+?)\"\:\s*\"([^"]*?)\"', str(v)):
      names.append((m.group(1), m.group(2)))

  print names
  print len(names)
  f.write(json.dumps(names))

