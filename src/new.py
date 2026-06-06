# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 12:09:31 2026

@author: daram
"""


import psycopg2
import pandas as pd
import numpy as np
from sqlalchemy import create_engine


DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "studentdb"
DB_USER = "postgres"
DB_PASSWORD = "james1859"

file_path = r"C:/Users/daram/Downloads/test (1) (1).csv"

# -----------------------------
print( "Insert sample rows into employees ")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
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

    # Sample rows to insert
    rows = [
        ("James", 25, "Data Engineering", 5000.00),
        ("Alice", 30, "IT", 6500.00),
        ("Bob", 28, "Finance", 5200.00)
    ]

    insert_query = """
    INSERT INTO employees (name, age, department, salary)
    VALUES (%s, %s, %s, %s);
    """

    cur.executemany(insert_query, rows)
    conn.commit()

    print("Sample rows inserted successfully into 'employees' table.")

    cur.close()
    conn.close()

except Exception as e:
    print("Error during Step 6:")
    print(e)



print(" Read employees table with psycopg2")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()

    cur.execute("SELECT * FROM employees;")
    rows = cur.fetchall()

    print("Rows currently inside employees table:")
    for row in rows:
        print(row)

    cur.close()
    conn.close()

except Exception as e:
    print("Error during Step 7:")
    print(e)



print("Read employees table into pandas ")

try:
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    df_employees = pd.read_sql("SELECT * FROM employees;", engine)

    print("Employees table as a DataFrame:")
    print(df_employees)

except Exception as e:
    print("Error during Step 8:")
    print(e)



print("Load CSV into PostgreSQL")

try:
    # Read the CSV file into pandas
    df_csv = pd.read_csv(file_path)

    print("Preview of CSV:")
    print(df_csv.head())

    print("\nCSV column names:")
    print(df_csv.columns.tolist())

    # Upload the CSV into PostgreSQL
    # if_exists='replace' means:
    # - if csv_table already exists, drop it and recreate it
    df_csv.to_sql(
        name="csv_table",
        con=engine,
        if_exists="replace",
        index=False
    )

    print("\nCSV uploaded successfully into PostgreSQL table 'csv_table'.")

except Exception as e:
    print("Error during Step 9:")
    print(e)


print("\nQuery csv_table")

try:
    query = "SELECT * FROM csv_table LIMIT 10;"
    result_df = pd.read_sql(query, engine)

    print("First 10 rows from csv_table:")
    print(result_df)

except Exception as e:
    print("Error during Step 10:")
    print(e)



print("\n manual row-by-row insert ")

try:
    
    df_manual = pd.read_csv(file_path)

    
    df_manual = df_manual.replace(np.nan, None)

    print("Preparing a manual insert version of the CSV...")
    print("Detected columns:", df_manual.columns.tolist())


    if len(df_manual.columns) >= 3:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()

       
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sample_table (
                col1 TEXT,
                col2 TEXT,
                col3 TEXT
            );
        """)
        conn.commit()

        # Optional: clear old rows so you do not duplicate data every time
        cur.execute("DELETE FROM sample_table;")
        conn.commit()

        # Insert row by row using the first 3 columns from the CSV
        for row in df_manual.itertuples(index=False):
            data = (
                None if row[0] is None else str(row[0]),
                None if row[1] is None else str(row[1]),
                None if row[2] is None else str(row[2])
            )

            cur.execute(
                "INSERT INTO sample_table (col1, col2, col3) VALUES (%s, %s, %s);",
                data
            )

        conn.commit()
        print("Manual row-by-row insert completed successfully into 'sample_table'.")

        # Show what was inserted
        cur.execute("SELECT * FROM sample_table LIMIT 10;")
        manual_rows = cur.fetchall()

        print("\nPreview of sample_table:")
        for r in manual_rows:
            print(r)

        cur.close()
        conn.close()

    else:
        print("Your CSV has fewer than 3 columns, so the sample_table demo was skipped.")

except Exception as e:
    print("Error during Step 11:")
    print(e)

