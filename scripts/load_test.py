"""
Load testing script for CockroachDB cluster study.
Runs continuous transactions and collects performance metrics.
"""
import psycopg2
import time
import statistics
import sys
from datetime import datetime
from typing import List

DSN_APP = "postgresql://root@localhost:26257/study_db?sslmode=disable"

class LoadTester:
    def __init__(self, report_interval=10):
        """
        Initialize load tester.

        Args:
            report_interval: Seconds between metric reports
        """
        self.report_interval = report_interval
        self.latencies: List[float] = []
        self.transaction_count = 0
        self.error_count = 0
        self.start_time = time.time()
        self.last_report_time = time.time()

    def run_transaction(self, conn) -> float:
        """
        Execute a single transaction and return its latency.

        Transaction includes:
        - Insert a new row
        - Read a few rows
        - Commit

        Returns:
            Latency in milliseconds
        """
        start = time.time()

        try:
            with conn.cursor() as cur:
                # Insert a new transaction
                user_id = self.transaction_count % 100
                amount = round((self.transaction_count % 1000) * 0.99, 2)

                cur.execute("""
                    INSERT INTO transactions (user_id, amount, description)
                    VALUES (%s, %s, %s);
                """, (user_id, amount, f"Load test transaction {self.transaction_count}"))

                # Read some recent transactions
                cur.execute("""
                    SELECT id, user_id, amount, created_at
                    FROM transactions
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT 5;
                """, (user_id,))

                rows = cur.fetchall()

            conn.commit()
            latency = (time.time() - start) * 1000  # Convert to ms
            return latency

        except Exception as e:
            conn.rollback()
            self.error_count += 1
            print(f"\n✗ Transaction error: {e}")
            return -1

    def calculate_metrics(self) -> dict:
        """Calculate current performance metrics."""
        if not self.latencies:
            return {}

        elapsed = time.time() - self.last_report_time
        total_elapsed = time.time() - self.start_time

        # Filter out failed transactions (-1 latency)
        valid_latencies = [lat for lat in self.latencies if lat > 0]

        if not valid_latencies:
            return {
                'tps': 0,
                'errors': len(self.latencies)
            }

        sorted_latencies = sorted(valid_latencies)
        n = len(sorted_latencies)

        return {
            'tps': len(self.latencies) / elapsed if elapsed > 0 else 0,
            'total_tps': self.transaction_count / total_elapsed if total_elapsed > 0 else 0,
            'transactions': len(self.latencies),
            'total_transactions': self.transaction_count,
            'errors': self.error_count,
            'p50': sorted_latencies[int(n * 0.50)] if n > 0 else 0,
            'p95': sorted_latencies[int(n * 0.95)] if n > 0 else 0,
            'p99': sorted_latencies[int(n * 0.99)] if n > 0 else 0,
            'min': min(sorted_latencies) if sorted_latencies else 0,
            'max': max(sorted_latencies) if sorted_latencies else 0,
            'avg': statistics.mean(sorted_latencies) if sorted_latencies else 0,
        }

    def print_metrics(self, metrics: dict, label: str = ""):
        """Print metrics in a formatted way."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n{'='*70}")
        print(f"[{timestamp}] {label}")
        print(f"{'='*70}")
        print(f"Transactions:    {metrics.get('transactions', 0):6d} (interval) | {metrics.get('total_transactions', 0):8d} (total)")
        print(f"TPS:             {metrics.get('tps', 0):6.1f} (interval) | {metrics.get('total_tps', 0):8.1f} (total)")
        print(f"Errors:          {metrics.get('errors', 0):6d}")
        print(f"-" * 70)
        print(f"Latency (ms):")
        print(f"  p50:           {metrics.get('p50', 0):6.2f}")
        print(f"  p95:           {metrics.get('p95', 0):6.2f}")
        print(f"  p99:           {metrics.get('p99', 0):6.2f}")
        print(f"  avg:           {metrics.get('avg', 0):6.2f}")
        print(f"  min:           {metrics.get('min', 0):6.2f}")
        print(f"  max:           {metrics.get('max', 0):6.2f}")
        print(f"{'='*70}\n")

    def run(self, duration: int = None):
        """
        Run the load test.

        Args:
            duration: Test duration in seconds (None = run indefinitely)
        """
        print(f"Starting load test...")
        print(f"Report interval: {self.report_interval} seconds")
        if duration:
            print(f"Duration: {duration} seconds")
        else:
            print(f"Duration: Continuous (Ctrl+C to stop)")
        print(f"\nConnecting to database...")

        try:
            conn = psycopg2.connect(DSN_APP)
            print("✓ Connected to CockroachDB\n")

            end_time = time.time() + duration if duration else None

            while True:
                # Check if we should stop
                if end_time and time.time() >= end_time:
                    break

                # Run transaction
                latency = self.run_transaction(conn)
                if latency > 0:
                    self.latencies.append(latency)
                self.transaction_count += 1

                # Report metrics at intervals
                if time.time() - self.last_report_time >= self.report_interval:
                    metrics = self.calculate_metrics()
                    self.print_metrics(metrics, f"Interval Report")

                    # Reset interval metrics
                    self.latencies = []
                    self.last_report_time = time.time()

            # Final report
            print("\n" + "="*70)
            print("FINAL REPORT")
            print("="*70)
            total_elapsed = time.time() - self.start_time
            print(f"Total runtime: {total_elapsed:.1f} seconds")
            print(f"Total transactions: {self.transaction_count}")
            print(f"Total errors: {self.error_count}")
            print(f"Average TPS: {self.transaction_count / total_elapsed:.1f}")
            print("="*70 + "\n")

            conn.close()

        except KeyboardInterrupt:
            print("\n\n✓ Load test stopped by user")

            # Print final metrics
            if self.latencies:
                metrics = self.calculate_metrics()
                self.print_metrics(metrics, "Final Metrics")

        except Exception as e:
            print(f"\n✗ Load test failed: {e}")
            raise


def main():
    """Main entry point."""
    # Parse command line arguments
    duration = None
    report_interval = 10

    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            print("Usage: python load_test.py [duration_seconds] [report_interval]")
            print("Example: python load_test.py 60 10  # Run for 60s, report every 10s")
            sys.exit(1)

    if len(sys.argv) > 2:
        try:
            report_interval = int(sys.argv[2])
        except ValueError:
            print("Invalid report interval")
            sys.exit(1)

    tester = LoadTester(report_interval=report_interval)
    tester.run(duration=duration)


if __name__ == "__main__":
    main()
