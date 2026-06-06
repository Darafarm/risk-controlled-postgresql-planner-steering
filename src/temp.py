from pathlib import Path

base = Path(r"C:\Users\daram\Desktop\SQL queries\join-order-benchmark-master\join-order-benchmark-master")

# find where .sql files are (up to 3 levels deep)
sql_files = list(base.glob("*.sql"))
sql_files += list(base.glob("*/*.sql"))
sql_files += list(base.glob("*/*/*.sql"))

print("Total .sql found:", len(sql_files))
print("First 20 files:")
for p in sql_files[:20]:
    print(p)