import psycopg2
import time
import random
import statistics
import uuid

# --- CONFIGURATION ---
DSN = "postgresql://root@localhost:26257/study_db?sslmode=disable"
PRINT_WINDOW = 10  # Print stats every 10 seconds

def setup_schema(conn):
    """Creates the table if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                value INT,
                created_at TIMESTAMP DEFAULT now()
            );
        """)
        # Create an index to test the "Online Indexing" experiment later
        # (We will add a secondary index manually during that experiment, 
        # so for now, we just stick to the base table).
    conn.commit()
    print("✅ Schema initialized.")

def run_load():
    """Runs the transaction loop and prints metrics."""
    conn = psycopg2.connect(DSN)
    setup_schema(conn)
    
    print(f"🚀 Load generator started. Printing stats every {PRINT_WINDOW} seconds...")
    print("Press CTRL+C to stop.")

    latencies = []
    start_window = time.time()
    
    try:
        while True:
            # 1. Start Timer
            t0 = time.time()

            # 2. The Transaction: Insert 1 row, Read 5 rows
            try:
                with conn.cursor() as cur:
                    # INSERT
                    val = random.randint(0, 1000)
                    cur.execute("INSERT INTO transactions (value) VALUES (%s)", (val,))
                    
                    # READ (simulating a read-heavy workload)
                    cur.execute("SELECT * FROM transactions ORDER BY created_at DESC LIMIT 5")
                    rows = cur.fetchall()
                
                conn.commit()
                
                # 3. Stop Timer & Record Latency (ms)
                latencies.append((time.time() - t0) * 1000)

            except psycopg2.OperationalError as e:
                # Handle retries for serialization failures (common in CRDB)
                conn.rollback()
                continue
            except Exception as e:
                print(f"Error: {e}")
                conn.rollback()
                time.sleep(1)

            # 4. Reporting Window
            now = time.time()
            if now - start_window >= PRINT_WINDOW:
                if not latencies:
                    continue

                # Calculate Metrics
                count = len(latencies)
                duration = now - start_window
                tps = count / duration
                
                # Percentiles
                latencies.sort()
                p50 = latencies[int(count * 0.50)]
                p95 = latencies[int(count * 0.95)]
                p99 = latencies[int(count * 0.99)]

                print(f"[{time.strftime('%H:%M:%S')}] "
                      f"TPS: {tps:.2f} | "
                      f"Latencies (ms) -> P50: {p50:.2f}, P95: {p95:.2f}, P99: {p99:.2f}")

                # Reset for next window
                latencies = []
                start_window = time.time()

    except KeyboardInterrupt:
        print("\n🛑 Load generator stopped.")
    finally:
        conn.close()

if __name__ == "__main__":
    run_load()