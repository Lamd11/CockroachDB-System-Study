"""
Helper script to add an index to the transactions table.
Use this during load testing to observe online schema changes.
"""
import psycopg2
import time

DSN_APP = "postgresql://root@localhost:26257/study_db?sslmode=disable"

def add_index():
    """Add an index on user_id and amount columns."""
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(DSN_APP)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        print("\n" + "="*60)
        print("ADDING INDEX: idx_user_amount ON (user_id, amount)")
        print("="*60)
        print("\nThis operation will happen ONLINE while traffic continues...")
        print("Monitor your load_test.py output for performance impact.\n")

        start = time.time()

        with conn.cursor() as cur:
            # Check if index already exists
            cur.execute("""
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = 'transactions'
                AND indexname = 'idx_user_amount';
            """)

            if cur.fetchone():
                print("✗ Index 'idx_user_amount' already exists!")
                print("\nTo drop it first, run:")
                print("  docker exec -it roach1 ./cockroach sql --insecure -d study_db")
                print("  DROP INDEX idx_user_amount;")
                return

            # Create index
            print("Creating index...")
            cur.execute("""
                CREATE INDEX idx_user_amount ON transactions(user_id, amount);
            """)

            elapsed = time.time() - start
            print(f"✓ Index created in {elapsed:.2f} seconds")

            # Show all indexes
            cur.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'transactions';
            """)

            print("\nAll indexes on 'transactions' table:")
            for row in cur.fetchall():
                print(f"  - {row[0]}")

        print("="*60)
        print("✓ Index addition complete!\n")

        conn.close()

    except Exception as e:
        print(f"\n✗ Failed to add index: {e}")
        raise


if __name__ == "__main__":
    add_index()
