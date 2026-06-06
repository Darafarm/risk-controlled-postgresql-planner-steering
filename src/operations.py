# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 11:57:54 2026

@author: daram
"""

import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="studentdb",
        user="postgres",
        password="your_password"
    )

    cur = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS employees (
        emp_id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        age INT,
        department VARCHAR(100),
        salary NUMERIC(10,2)
    );
    """

    cur.execute(create_table_query)
    conn.commit()

    print("Table 'employees' created successfully!")

    cur.close()
    conn.close()

except Exception as e:
    print("Error creating table:")
    print(e)