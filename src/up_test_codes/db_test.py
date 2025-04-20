import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host='postgres',
    dbname='news',
    user=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD")
)

cur = conn.cursor()
cur.execute("SELECT * FROM news_article")
rows = cur.fetchall()

for r in rows:
    print(r)

cur.close()
conn.close()
