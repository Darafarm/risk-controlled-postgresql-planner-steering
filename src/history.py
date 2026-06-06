# -*- coding: utf-8 -*-
# *** Spyder Python Console History Log ***

## ---(Fri Feb 27 09:24:32 2026)---
%runfile C:/Users/daram/.spyder-py3/testing_pathway.py --wdir
%runfile C:/Users/daram/.spyder-py3/untitled2.py --wdir
%runcell -i 0 C:/Users/daram/.spyder-py3/untitled2.py
%runfile C:/Users/daram/.spyder-py3/db_test.py --wdir
%runfile C:/Users/daram/.spyder-py3/job_runner_10queries.py --wdir
%runfile C:/Users/daram/.spyder-py3/untitled4.py --wdir
%runfile C:/Users/daram/.spyder-py3/job_runner_10queries.py --wdir
%runcell -i 0 C:/Users/daram/.spyder-py3/job_runner_10queries.py
%runfile C:/Users/daram/.spyder-py3/job_runner_10queries.py --wdir
%runcell -i 0 C:/Users/daram/.spyder-py3/untitled4.py
%runfile C:/Users/daram/.spyder-py3/untitled4.py --wdir
%runfile C:/Users/daram/.spyder-py3/job_runner_10queries.py --wdir
%runfile C:/Users/daram/.spyder-py3/untitled4.py --wdir

## ---(Fri Mar  6 16:44:41 2026)---
%runcell -i 0 C:/Users/daram/.spyder-py3/untitled0.py
%runfile C:/Users/daram/.spyder-py3/ML_dataset.py --wdir
%runcell -i 0 C:/Users/daram/.spyder-py3/ML_dataset.py
pip install psycopg2-binary
%runfile C:/Users/daram/.spyder-py3/ML_dataset.py --wdir
cls
%runfile C:/Users/daram/.spyder-py3/ML_dataset.py --wdir
cls
%runfile C:/Users/daram/.spyder-py3/ML_dataset.py --wdir
%runfile C:/Users/daram/.spyder-py3/untitled1.py --wdir
%runfile C:/Users/daram/.spyder-py3/untitled2.py --wdir
%runfile C:/Users/daram/.spyder-py3/ML_dataset.py --wdir
%runfile C:/Users/daram/.spyder-py3/untitled3.py --wdir
cls
%runfile C:/Users/daram/.spyder-py3/untitled3.py --wdir




DB_HOST = "127.0.0.1"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASSWORD = "JamesDB2026!"   # 
DB_NAME = "imdb"

# ============================
# TEST DATABASE CONNECTION
# ============================
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )
    
    print("Connected successfully with psycopg2!")
    
    conn.close()

except Exception as e:
    print("Direct connection failed.")
    print("Error:", e)
%runfile C:/Users/daram/.spyder-py3/untitled3.py --wdir
cls
%runfile C:/Users/daram/.spyder-py3/untitled3.py --wdir
%runfile C:/Users/daram/.spyder-py3/untitled1.py --wdir
%runcell -i 0 C:/Users/daram/.spyder-py3/untitled1.py
features = [
    "startup_cost",
    "total_cost",
    "plan_rows",
    "plan_width",
    "actual_rows",
    "actual_total_time"
]

X = df[features]
y = df["oracle_arm"]

print("Label distribution:")
print(y.value_counts())
%runcell -i 0 C:/Users/daram/.spyder-py3/untitled1.py
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(X_train.shape)
print(X_test.shape)
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42

from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print("Sample predictions:")
print(y_pred[:10])
from sklearn.metrics import accuracy_score, classification_report

print("Accuracy:", accuracy_score(y_test, y_pred))

print(classification_report(y_test, y_pred))
import pandas as pd

importance = pd.Series(
    model.feature_importances_,
    index=features
).sort_values(ascending=False)

print("Feature importance:")
print(importance)
results = X_test.copy()

results["true_oracle"] = y_test
results["predicted_arm"] = y_pred

results.to_csv("planner_predictions.csv", index=False)

## ---(Thu Mar 12 20:15:01 2026)---
%runfile C:/Users/daram/.spyder-py3/job_runner_for_all_q.py --wdir
%runfile C:/Users/daram/.spyder-py3/untitled0.py --wdir
cls
%runfile C:/Users/daram/.spyder-py3/untitled0.py --wdir
cls
%runfile C:/Users/daram/.spyder-py3/untitled0.py --wdir
%runcell -i 0 C:/Users/daram/.spyder-py3/untitled1.py
%runfile C:/Users/daram/.spyder-py3/training_queries.py --wdir
%runfile C:/Users/daram/.spyder-py3/untitled1.py --wdir
pip install pyscenic
results = X_test.copy()

results["true_oracle"] = y_test
results["predicted_arm"] = y_pred

results.to_csv("planner_predictions.csv", index=False)

$ conda create --name scenicplus python=3.11 -y
$ conda activate scenicplus
$ git clone https://github.com/aertslab/scenicplus
$ cd scenicplus
$ pip install .
conda create --name scenicplus python=3.11 -y
conda activate scenicplus
git clone https://github.com/aertslab/scenicplus
cd scenicplus
pip install .
import scenicplus
print("SCENIC+ imported successfully")
import scenicplus
print(scenicplus.__version__)
%runfile C:/Users/daram/.spyder-py3/untitled2.py --wdir

## ---(Tue Mar 17 13:17:19 2026)---
pip install mysql.connector 
%runfile C:/Users/daram/.spyder-py3/untitled0.py --wdir
import mysql.connector
import keyring
import pandas as pd
import numpy as np
config = {
    'user': 'root',
    'password': keyring.get_password("SQLServer", "Dbadmin"),
    'host': 'localhost',
}
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

# create database if it does not exist
cursor.execute("CREATE DATABASE IF NOT EXISTS [Database Name];")

# reconnect with the new database
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

try:
    cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS [Table Name] (
            [Attribute 1] [DataType],
            [Attribute 2] [DataType],
            ...
            PRIMARY KEY (Attribute k)
            );
            """
        )
except:
    print("error in creating table")
import pyodbc
import keyring
import pandas as pd
import numpy as np


server = 'localhost'         
database = 'DatabaseName'
username = 'sa'              
password = keyring.get_password("SQLServer", "Dbadmin")

# Connect to SQL Server master first
conn_str_master = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE=master;"
    f"UID={username};"
    f"PWD={password};"
)
cnx = pyodbc.connect(conn_str_master, autocommit=True)
cursor = cnx.cursor()
%runcell -i 0 C:/Users/daram/.spyder-py3/untitled2.py
%runfile C:/Users/daram/.spyder-py3/untitled2.py --wdir
import mysql.connector
import keyring
import pandas as pd
import numpy as np

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()
config = {
    'user': 'root',
    'password': keyring.get_password("MySQL", "Dbadmin"),
    'host': 'localhost',
}

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

# create database if it does not exist
cursor.execute("CREATE DATABASE IF NOT EXISTS [test];")

# reconnect with the new database
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()
%runfile C:/Users/daram/.spyder-py3/untitled3.py --wdir
%runfile C:/Users/daram/.spyder-py3/est_conn.py --wdir
%runfile C:/Users/daram/.spyder-py3/create_table.py --wdir
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
%runfile C:/Users/daram/.spyder-py3/untitled6.py --wdir
import os
print(os.getcwd())
%runfile C:/Users/daram/.spyder-py3/untitled6.py --wdir
%runfile C:/Users/daram/.spyder-py3/untitled7.py --wdir
%runfile C:/Users/daram/.spyder-py3/untitled8.py --wdir
%runfile C:/Users/daram/.spyder-py3/untitled9.py --wdir
%runfile C:/Users/daram/.spyder-py3/untitled8.py --wdir
%runfile C:/Users/daram/.spyder-py3/untitled9.py --wdir
%runfile C:/Users/daram/.spyder-py3/untitled10.py --wdir
import psycopg2

tables_to_check = [
    "aka_name", "aka_title", "cast_info", "char_name", "company_name",
    "company_type", "complete_cast", "info_type", "keyword", "kind_type",
    "link_type", "movie_companies", "movie_info", "movie_info_idx",
    "movie_keyword", "movie_link", "name", "person_info", "role_type", "title"
]

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="imdb",
    user="postgres",
    password="james1859"
)

cur = conn.cursor()

for table in tables_to_check:
    cur.execute(f"SELECT COUNT(*) FROM {table};")
    count = cur.fetchone()[0]
    print(f"{table}: {count}")

cur.close()
conn.close()
%runfile C:/Users/daram/.spyder-py3/untitled10.py --wdir
%runfile C:/Users/daram/.spyder-py3/untitled11.py --wdir

## ---(Sat Apr 11 12:05:56 2026)---
%runcell -i 0 'C:/Users/daram/Desktop/RDMBS/Relational DBMS ML/dd/train_model.py'
%runfile C:/Users/daram/.spyder-py3/untitled6.py --wdirpip install xgboost
pip install xgboost
%runfile 'C:/Users/daram/Desktop/RDMBS/Relational DBMS ML/dd/train_model.py' --wdir
%runfile 'C:/Users/daram/Desktop/RDMBS/Relational DBMS ML/dd/untitled13.py' --wdir

## ---(Tue Jun  2 15:57:55 2026)---
%runfile C:/Users/daram/.spyder-py3/untitled12.py --wdir
pip install pymongo
%runfile C:/Users/daram/.spyder-py3/untitled12.py --wdir
%runcell -i 0 C:/Users/daram/.spyder-py3/untitled12.py
result = collection.find_one({"name": "James"})
print("Found document:")
print(result)
print("Inserted successfully")
print("Total documents:", collection.count_documents({}))
%runcell -i 0 C:/Users/daram/.spyder-py3/untitled12.py
collection.insert_one({
    "name": "Seyi",
    "visited_doctor": "Dr. Brandley",
    "prescribed_drug": "Tylenol",
    "hospital": "Hospital Y"
})

result = collection.find_one({"name": "Seyi"})
print("Found document:")
print(result)
collection.insert_many([
    {"name": "Alice", "visited_doctor": "Dr. Priya", 
     "prescribed_drug": "Ibuprofen", "hospital": "Hospital Y"},
    {"name": "Bob", "visited_doctor": "Dr. Amina", 
     "prescribed_drug": "Penicillin", "hospital": "Hospital X"},
    {"name": "Sara", "visited_doctor": "Dr. Priya", 
     "prescribed_drug": "Amoxicillin", "hospital": "Hospital Z"},
    {"name": "Musa", "visited_doctor": "Dr. James", 
     "prescribed_drug": "Ibuprofen", "hospital": "Hospital X"},
])

print("All patients at Hospital X:")
for doc in collection.find({"hospital": "Hospital X"}):
    print(" -", doc["name"], "saw", doc["visited_doctor"])

print()
print("Everyone prescribed Amoxicillin:")
for doc in collection.find({"prescribed_drug": "Amoxicillin"}):
    print(" -", doc["name"])
print("All patients at Hospital X:")
for doc in collection.find({"hospital": "Hospital Y"}):
    print(" -", doc["name"], "saw", doc["visited_doctor"])
%runcell -i 0 C:/Users/daram/.spyder-py3/untitled12.py
print("=== All documents in your collection ===")
for doc in collection.find():
    print(doc)

print()
print("Total documents:", collection.count_documents({}))
print("=== All unique doctor-patient relationships ===")
for doc in collection.find(
    {"visited_doctor": {"$exists": True}},
    {"name": 1, "visited_doctor": 1, "hospital": 1, "_id": 0}
):
    print(f"  {doc.get('name')} → {doc.get('visited_doctor')} @ {doc.get('hospital')}")
%runcell -i 0 C:/Users/daram/.spyder-py3/untitled12.py
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["research_db"]
collection = db["entities"]

collection.drop()
print("Collection cleared")

collection.insert_many([
    {"name": "James", "visited_doctor": "Dr. Amina", 
     "prescribed_drug": "Amoxicillin", "hospital": "Hospital X"},
    {"name": "Seyi", "visited_doctor": "Dr. Brandley", 
     "prescribed_drug": "Tylenol", "hospital": "Hospital Y"},
    {"name": "Alice", "visited_doctor": "Dr. Priya", 
     "prescribed_drug": "Ibuprofen", "hospital": "Hospital Y"},
    {"name": "Bob", "visited_doctor": "Dr. Amina", 
     "prescribed_drug": "Penicillin", "hospital": "Hospital X"},
    {"name": "Sara", "visited_doctor": "Dr. Priya", 
     "prescribed_drug": "Amoxicillin", "hospital": "Hospital Z"},
    {"name": "Musa", "visited_doctor": "Dr. James", 
     "prescribed_drug": "Ibuprofen", "hospital": "Hospital X"},
])

print("Clean dataset inserted")
print("Total documents:", collection.count_documents({}))
pipeline = [
    {
        "$match": {
            "visited_doctor": {"$exists": True}
        }
    },
    {
        "$project": {
            "_id": 0,
            "entity_1": "$name",
            "relation": "visited",
            "entity_2": "$visited_doctor"
        }
    }
]

results = list(collection.aggregate(pipeline))

print("=== Candidate semantic edges extracted from documents ===")
print()
for r in results:
    print(f"  {r['entity_1']}  --[{r['relation']}]-->  {r['entity_2']}")

print()
print(f"Total candidate edges found: {len(results)}")
def score_confidence(relation_type, source_field):
    """
    Assigns a confidence score to a candidate edge.
    
    Logic:
    - Direct field (dedicated key in document) = high confidence
    - Co-occurrence (two things appear in same doc) = medium confidence
    - Inferred (we are guessing the relationship) = low confidence
    """
    scores = {
        "VISITED":     0.95,
        "TREATED_AT":  0.90,
        "PRESCRIBED":  0.75,
        "WORKS_AT":    0.60,
        "LOCATED_IN":  0.55,
    }
    return scores.get(relation_type, 0.50)

pipeline_visited = [
    {"$match": {"visited_doctor": {"$exists": True}}},
    {"$project": {
        "_id": 0,
        "entity_1": "$name",
        "relation": "VISITED",
        "entity_2": "$visited_doctor"
    }}
]

pipeline_prescribed = [
    {"$match": {"prescribed_drug": {"$exists": True}}},
    {"$project": {
        "_id": 0,
        "entity_1": "$visited_doctor",
        "relation": "PRESCRIBED",
        "entity_2": "$prescribed_drug"
    }}
]

pipeline_treated_at = [
    {"$match": {"hospital": {"$exists": True}}},
    {"$project": {
        "_id": 0,
        "entity_1": "$name",
        "relation": "TREATED_AT",
        "entity_2": "$hospital"
    }}
]

all_edges = (
    list(collection.aggregate(pipeline_visited)) +
    list(collection.aggregate(pipeline_prescribed)) +
    list(collection.aggregate(pipeline_treated_at))
)

print("=== Candidate edges with confidence scores ===")
print()
print(f"{'Entity 1':<15} {'Relation':<15} {'Entity 2':<15} {'Confidence'}")
print("-" * 60)

scored_edges = []
for edge in all_edges:
    confidence = score_confidence(edge['relation'], None)
    edge['confidence'] = confidence
    scored_edges.append(edge)
    print(f"{edge['entity_1']:<15} {edge['relation']:<15} {edge['entity_2']:<15} {confidence}")

print()
print(f"Total candidate edges: {len(scored_edges)}")












entity_counts = defaultdict(int)

# Loop through every document in the collection
for doc in collection.find():
    
    # Check each field that contains an entity name
    # For each field that exists in this document,
    # add 1 to the count for that entity
    
    if "name" in doc:
        entity_counts[doc["name"]] += 1
    
    if "visited_doctor" in doc:
        entity_counts[doc["visited_doctor"]] += 1
    
    if "prescribed_drug" in doc:
        entity_counts[doc["prescribed_drug"]] += 1
    
    if "hospital" in doc:
        entity_counts[doc["hospital"]] += 1

# Print the results sorted by count, highest first
print("=== How often each entity appears ===")
print()

# sorted() sorts a list. key=lambda x: -x[1] means
# sort by the second item (the count) in reverse order
for entity, count in sorted(entity_counts.items(), 
                             key=lambda x: -x[1]):
    print(f"  {entity:<20} appears {count} time(s)")

print()
from collections import defaultdict
from collections import defaultdict
entity_counts = defaultdict(int)

# Loop through every document in the collection
for doc in collection.find():
    
    # Check each field that contains an entity name
    # For each field that exists in this document,
    # add 1 to the count for that entity
    
    if "name" in doc:
        entity_counts[doc["name"]] += 1
    
    if "visited_doctor" in doc:
        entity_counts[doc["visited_doctor"]] += 1
    
    if "prescribed_drug" in doc:
        entity_counts[doc["prescribed_drug"]] += 1
    
    if "hospital" in doc:
        entity_counts[doc["hospital"]] += 1

# Print the results sorted by count, highest first
print("=== How often each entity appears ===")
print()

# sorted() sorts a list. key=lambda x: -x[1] means
# sort by the second item (the count) in reverse order
for entity, count in sorted(entity_counts.items(), 
                             key=lambda x: -x[1]):
    print(f"  {entity:<20} appears {count} time(s)")

print()
COUNT HOW OFTEN EACH RELATIONSHIP APPEARS
#
# Now we count how many times each specific triple appears.
# A triple is: (entity_1, relation_type, entity_2)
#
# Example triple: ("James", "VISITED", "Dr. Amina")
#
# If this triple appears in 3 different documents,
# we are much more confident it is a real relationship
# than if it appears only once.

relation_counts = defaultdict(int)

for doc in collection.find():
    
    # VISITED relationship: patient visited a doctor
    # We only count it if BOTH fields exist in this document
    if "name" in doc and "visited_doctor" in doc:
        
        # Create a tuple (immutable list) as the key
        # Tuples can be dictionary keys, lists cannot
        triple = (doc["name"], "VISITED", doc["visited_doctor"])
        relation_counts[triple] += 1
    
    # PRESCRIBED relationship: doctor prescribed a drug
    if "visited_doctor" in doc and "prescribed_drug" in doc:
        triple = (doc["visited_doctor"], "PRESCRIBED", 
                  doc["prescribed_drug"])
        relation_counts[triple] += 1
    
    # TREATED_AT relationship: patient treated at hospital
    if "name" in doc and "hospital" in doc:
        triple = (doc["name"], "TREATED_AT", doc["hospital"])
        relation_counts[triple] += 1

print("=== How often each relationship appears ===")
print()

for (e1, rel, e2), count in sorted(relation_counts.items(), 
                                    key=lambda x: -x[1]):
    print(f"  {e1} --[{rel}]--> {e2}  "
          f"(seen {count} time(s))")

print()











relation_counts = defaultdict(int)

for doc in collection.find():
    
    # VISITED relationship: patient visited a doctor
    # We only count it if BOTH fields exist in this document
    if "name" in doc and "visited_doctor" in doc:
        
        # Create a tuple (immutable list) as the key
        # Tuples can be dictionary keys, lists cannot
        triple = (doc["name"], "VISITED", doc["visited_doctor"])
        relation_counts[triple] += 1
    
    # PRESCRIBED relationship: doctor prescribed a drug
    if "visited_doctor" in doc and "prescribed_drug" in doc:
        triple = (doc["visited_doctor"], "PRESCRIBED", 
                  doc["prescribed_drug"])
        relation_counts[triple] += 1
    
    # TREATED_AT relationship: patient treated at hospital
    if "name" in doc and "hospital" in doc:
        triple = (doc["name"], "TREATED_AT", doc["hospital"])
        relation_counts[triple] += 1

print("=== How often each relationship appears ===")
print()

for (e1, rel, e2), count in sorted(relation_counts.items(), 
                                    key=lambda x: -x[1]):
    print(f"  {e1} --[{rel}]--> {e2}  "
          f"(seen {count} time(s))")

print()










def score_confidence(entity_1, relation, entity_2):
    """
    Returns a confidence score between 0.0 and 1.0
    for a candidate semantic edge.
    
    Parameters:
        entity_1     : source entity name (e.g. "James")
        relation     : relationship type (e.g. "VISITED")
        entity_2     : target entity name (e.g. "Dr. Amina")
    
    Returns:
        float between 0.0 and 1.0
    """
    
    # ── Signal 1: Base score by relation type ──
    # How directly was this relationship stated 
    # in the original document?
    # VISITED = 0.90 because it came from a dedicated field
    # PRESCRIBED = 0.70 because we inferred the doctor 
    #              prescribed the drug (slightly less direct)
    # TREATED_AT = 0.85 because hospital field is explicit
    
    base_scores = {
        "VISITED":    0.90,
        "TREATED_AT": 0.85,
        "PRESCRIBED": 0.70,
        "WORKS_AT":   0.55,
    }
    
    # .get(relation, 0.50) means: look up this relation type.
    # If it is not in the dictionary, return 0.50 as default.
    base = base_scores.get(relation, 0.50)
    
    
    # ── Signal 2: Entity frequency score ──
    # How often do the two entities appear in the dataset?
    # More appearances = more trustworthy entity
    
    # Get the count for each entity (default 0 if not found)
    freq_1 = entity_counts.get(entity_1, 0)
    freq_2 = entity_counts.get(entity_2, 0)
    
    # Find the maximum frequency in the whole dataset
    # We use this to normalise scores to 0-1 range
    max_freq = max(entity_counts.values())
    
    # Average the two entity frequencies
    # then divide by the maximum to get a 0-1 score
    # Example: freq_1=2, freq_2=3, max=6
    # entity_score = ((2+3)/2) / 6 = 2.5/6 = 0.42
    entity_score = ((freq_1 + freq_2) / 2) / max_freq
    
    
    # ── Signal 3: Relationship frequency score ──
    # How many times have we seen this exact triple?
    
    triple = (entity_1, relation, entity_2)
    rel_freq = relation_counts.get(triple, 0)
    
    # Normalise by the maximum relationship frequency
    max_rel = max(relation_counts.values())
    relation_score = rel_freq / max_rel
    
    
    # ── Combine all three signals ──
    # Weighted average:
    # 50% from relation type (strongest signal)
    # 30% from entity frequency
    # 20% from relationship frequency
    
    final_score = (
        0.50 * base +          
        0.30 * entity_score +  
        0.20 * relation_score  
    )
    
    # round() to 3 decimal places for clean display
    return round(final_score, 3)


print("Confidence scorer defined successfully")
print()







pipeline_visited = [
    # Stage 1: only process docs that have visited_doctor
    {"$match": {"visited_doctor": {"$exists": True}}},
    
    # Stage 2: reshape each doc into an edge structure
    {"$project": {
        "_id": 0,
        "entity_1": "$name",
        "relation": "VISITED",
        "entity_2": "$visited_doctor"
    }}
]

# Extract PRESCRIBED edges
pipeline_prescribed = [
    {"$match": {"prescribed_drug": {"$exists": True}}},
    {"$project": {
        "_id": 0,
        "entity_1": "$visited_doctor",
        "relation": "PRESCRIBED",
        "entity_2": "$prescribed_drug"
    }}
]

# Extract TREATED_AT edges
pipeline_treated_at = [
    {"$match": {"hospital": {"$exists": True}}},
    {"$project": {
        "_id": 0,
        "entity_1": "$name",
        "relation": "TREATED_AT",
        "entity_2": "$hospital"
    }}
]

# Combine all three lists of edges into one list
# The + operator joins lists together
all_edges = (
    list(collection.aggregate(pipeline_visited)) +
    list(collection.aggregate(pipeline_prescribed)) +
    list(collection.aggregate(pipeline_treated_at))
)

print(f"Extracted {len(all_edges)} total candidate edges")
print()





scored_edges = []

for edge in all_edges:
    
    # Call the scorer function for this edge
    confidence = score_confidence(
        edge['entity_1'],  # source entity
        edge['relation'],  # relationship type
        edge['entity_2']   # target entity
    )
    
    # Add the score to the edge dictionary
    # This is just adding a new key to the Python dict
    edge['confidence'] = confidence
    
    # Add to our list of scored edges
    scored_edges.append(edge)

# Sort edges by confidence score, highest first
# key=lambda x: -x['confidence'] sorts in descending order
scored_edges.sort(key=lambda x: -x['confidence'])

print("=== All candidate edges with confidence scores ===")
print()
print(f"{'Entity 1':<15} {'Relation':<15} "
      f"{'Entity 2':<15} {'Score':<8} {'Bar'}")
print("-" * 70)

for edge in scored_edges:
    
    # Create a simple visual bar
    # int(score * 20) gives a bar 0-20 chars wide
    # A score of 1.0 = 20 blocks, 0.5 = 10 blocks
    bar = "█" * int(edge['confidence'] * 20)
    
    print(f"{edge['entity_1']:<15} "
          f"{edge['relation']:<15} "
          f"{edge['entity_2']:<15} "
          f"{edge['confidence']:<8} "
          f"{bar}")

print()
print(f"Highest confidence edge: {scored_edges[0]}")
print(f"Lowest confidence edge:  {scored_edges[-1]}")