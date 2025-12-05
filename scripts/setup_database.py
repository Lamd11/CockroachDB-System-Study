"""
Setup script for CockroachDB cluster study.
Creates the database and initial schema.
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DSN_ADMIN = "postgresql://root@localhost:26257/defaultdb?sslmode=disable"
DSN_APP = "postgresql://root@localhost:26257/study_db?sslmode=disable"

def setup_database():
    """Create database and schema for the study."""
    try:
        # Create database
        print("Connecting to CockroachDB...")
        conn_admin = psycopg2.connect(DSN_ADMIN)
        conn_admin.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with conn_admin.cursor() as cur:
            cur.execute("CREATE DATABASE IF NOT EXISTS study_db;")
            print("✓ Database 'study_db' created")

        conn_admin.close()

        # Create table
        conn_app = psycopg2.connect(DSN_APP)
        conn_app.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with conn_app.cursor() as cur:
            # Drop table if exists (for clean reruns)
            cur.execute("DROP TABLE IF EXISTS transactions CASCADE;")

            # Create transactions table
            cur.execute("""
                CREATE TABLE transactions (
                    id SERIAL PRIMARY KEY,
                    user_id INT NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            print("✓ Table 'transactions' created")

            # Insert some initial data
            for i in range(100):
                cur.execute("""
                    INSERT INTO transactions (user_id, amount, description)
                    VALUES (%s, %s, %s);
                """, (i % 10, round(10.50 * (i + 1), 2), f"Initial transaction {i}"))

            print("✓ Inserted 100 initial rows")

            # Show table info
            cur.execute("SELECT COUNT(*) FROM transactions;")
            count = cur.fetchone()[0]
            print(f"✓ Total rows in transactions: {count}")

        conn_app.close()
        print("\n✓ Setup complete! Ready to run load tests.")

    except Exception as e:
        print(f"✗ Setup failed: {e}")
        raise

if __name__ == "__main__":
    setup_database()
