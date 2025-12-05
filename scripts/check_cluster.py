"""
Quick cluster health check script.
Verifies cluster status and displays key information.
"""
import psycopg2
import sys

DSN_APP = "postgresql://root@localhost:26257/study_db?sslmode=disable"

def check_cluster():
    """Check cluster health and display key metrics."""
    try:
        print("Connecting to CockroachDB cluster...")
        conn = psycopg2.connect(DSN_APP)

        with conn.cursor() as cur:
            # Check table exists and row count
            print("\n" + "="*60)
            print("DATABASE STATUS")
            print("="*60)

            cur.execute("SELECT COUNT(*) FROM transactions;")
            count = cur.fetchone()[0]
            print(f"Total transactions in database: {count:,}")

            # Check if index exists
            cur.execute("""
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = 'transactions'
                AND indexname != 'transactions_pkey';
            """)
            indexes = cur.fetchall()

            if indexes:
                print(f"Indexes on 'transactions' table:")
                for idx in indexes:
                    print(f"  - {idx[0]}")
            else:
                print("No secondary indexes on 'transactions' table")

            # Get node count (requires internal tables)
            try:
                cur.execute("""
                    SELECT count(*)
                    FROM crdb_internal.gossip_liveness
                    WHERE updated_at > now() - INTERVAL '10 seconds';
                """)
                live_nodes = cur.fetchone()[0]
                print(f"\nLive nodes: {live_nodes}")
            except:
                print("\nNode count: Unable to determine (requires cluster access)")

            print("="*60)
            print("\n✓ Cluster is healthy and accessible\n")

        conn.close()
        return True

    except psycopg2.OperationalError as e:
        print(f"\n✗ Cannot connect to cluster")
        print(f"Error: {e}")
        print("\nMake sure:")
        print("  1. Docker containers are running: docker ps")
        print("  2. Cluster is initialized: docker exec -it roach1 ./cockroach init --insecure")
        print("  3. Database is set up: python scripts/setup_database.py")
        return False

    except Exception as e:
        print(f"\n✗ Cluster check failed: {e}")
        return False


if __name__ == "__main__":
    success = check_cluster()
    sys.exit(0 if success else 1)
