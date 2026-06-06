# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 13:29:31 2026

@author: daram
"""

import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="studentdb",
        user="postgres",
        password="james1859"
    )
    print("Connected to studentdb successfully!")

    cur = conn.cursor()
    cur.execute("SELECT current_database();")
    print("Current database:", cur.fetchone()[0])

    cur.close()
    conn.close()

except Exception as e:
    print("Connection failed:")
    print(e)