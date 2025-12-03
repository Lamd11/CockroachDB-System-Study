import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Used to create the DB
DSN_ADMIN = "postgresql://root@localhost:26257/defaultdb?sslmode=disable"

# App Connection 
DSN_APP = "postgresql://root@localhost:26257/study_db?sslmode=disable"

def run_test():
    try:
        conn_admin = psycopg2.connect(DSN_ADMIN)
        conn_admin.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn_admin.cursor() as cur:
            cur.execute("CREATE DATABASE IF NOT EXISTS study_db;")
        
        conn_admin.close()
        print("Database created")

        conn_app = psycopg2.connect(DSN_APP)

        print("Success")
        conn_app.close()

    except Exception as e:
        print(f"Failed:")

if __name__ == "__main__":
    run_test()