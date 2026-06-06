# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 09:40:22 2026

@author: daram
"""




import psycopg2


HOST = "localhost"
PORT = 5432
DBNAME = "imdb"      
USER = "postgres"        
PASSWORD = "james1859"           
# --------------------------------

try:
    conn = psycopg2.connect(
        host=HOST,
        port=PORT,
        dbname=DBNAME,
        user=USER,
        password=PASSWORD
    )

    print("Connection successful!")

    cur = conn.cursor()
    cur.execute("SELECT current_database();")
    print("Connected to database:", cur.fetchone()[0])

    cur.close()
    conn.close()

except Exception as e:
    print("Connection failed:")
    print(e)