# CockroachDB Cluster Testing Instructions

This guide provides step-by-step instructions for running the CockroachDB distributed system study. Follow each test in order and record your observations.

## Prerequisites

Before starting, ensure:
- Docker Desktop is running
- Python virtual environment is activated: `source venv/bin/activate`
- All dependencies are installed: `pip install -r requirements.txt`

## Initial Setup

### 1. Start the 3-Node Cluster

```bash
# Start initial 3-node cluster (roach1, roach2, roach3)
docker-compose up -d roach1 roach2 roach3

# Wait 10 seconds for nodes to start
sleep 10

# Initialize the cluster (only needed once)
docker exec -it roach1 ./cockroach init --insecure
```

### 2. Verify Cluster is Running

Open the CockroachDB Admin UI in your browser:
```
http://localhost:8080
```

Check that all 3 nodes show as "Live" in the Overview page.

### 3. Initialize Database and Schema

```bash
python scripts/setup_database.py
```

You should see:
```
✓ Database 'study_db' created
✓ Table 'transactions' created
✓ Inserted 100 initial rows
✓ Setup complete!
```

---

## Test 1: Baseline Load Test

**Goal:** Establish baseline performance metrics with 3 nodes.

### Steps:

1. **Start the load test** (runs for 60 seconds, reports every 10 seconds):
   ```bash
   python scripts/load_test.py 60 10
   ```

2. **Record the metrics** from the output:
   - Transactions Per Second (TPS)
   - Latency: p50, p95, p99
   - Error count (should be 0)

3. **Take a screenshot** of the Admin UI showing:
   - Overview page with 3 live nodes
   - SQL Dashboard showing query activity

### Expected Results:
- Stable TPS throughout the test
- Low latency (typically <50ms for p99)
- No errors

### What to Observe:
- How CRDB distributes data across the 3 nodes
- Look at "Ranges" in the Admin UI to see data replication

---

## Test 2: Scale-Out (3 → 5 Nodes)

**Goal:** Demonstrate CRDB's ability to scale horizontally while handling traffic.

### Steps:

1. **Start continuous load test** in Terminal 1:
   ```bash
   python scripts/load_test.py
   ```
   (Press Ctrl+C to stop when done)

2. **In a new terminal (Terminal 2)**, add two more nodes:
   ```bash
   docker-compose up -d roach4 roach5
   ```

3. **Watch the Admin UI** for 2-3 minutes:
   - Go to Metrics → Replication Dashboard
   - Observe ranges being redistributed to new nodes

4. **Record metrics** before and after:
   - Note TPS and latency BEFORE adding nodes (from first interval report)
   - Wait 2-3 minutes for cluster to stabilize
   - Note TPS and latency AFTER rebalancing completes

5. **Stop the load test** (Ctrl+C in Terminal 1)

### Expected Results:
- TPS may dip slightly during rebalancing, then recover
- Latency should remain stable or improve slightly
- No errors
- Data eventually spreads across all 5 nodes

### What to Observe:
- **Ranges moving**: Admin UI → Metrics → Replication Dashboard
- **Leaseholder distribution**: How CRDB balances leadership
- **System resilience**: Transactions continue during scale-out

---

## Test 3: Online Schema Change (Add Index)

**Goal:** Show CRDB can add an index without downtime.

### Steps:

1. **Start continuous load test** in Terminal 1:
   ```bash
   python scripts/load_test.py
   ```

2. **In Terminal 2, connect to the database**:
   ```bash
   docker exec -it roach1 ./cockroach sql --insecure --database=study_db
   ```

3. **Check metrics BEFORE adding index** (note TPS and latency from Terminal 1)

4. **Create the index** (in Terminal 2 SQL prompt):
   ```sql
   CREATE INDEX idx_user_amount ON transactions(user_id, amount);
   ```

5. **Monitor the load test output** in Terminal 1:
   - Watch for latency spikes during index creation
   - Note any TPS changes

6. **Check index status** (in Terminal 2):
   ```sql
   SHOW INDEXES FROM transactions;
   ```

7. **After index completes**, record final metrics from Terminal 1

8. **Stop the load test** (Ctrl+C) and **exit SQL** (`\q`)

### Expected Results:
- Small latency increase during index creation
- TPS may dip slightly during index build
- No errors or transaction failures
- After completion, metrics return to normal or improve (faster reads)

### What to Observe:
- **Online DDL**: Transactions continue during schema change
- **Performance impact**: Temporary increase in latency
- **Recovery**: System returns to baseline after index completes

---

## Test 4: Node Failure Simulation

**Goal:** Demonstrate CRDB's fault tolerance and automatic recovery.

### Steps:

1. **Start continuous load test** in Terminal 1:
   ```bash
   python scripts/load_test.py
   ```

2. **Record baseline metrics** (first 10-20 seconds)

3. **In Terminal 2, kill one node**:
   ```bash
   docker stop roach3
   ```

4. **Observe the load test**:
   - Watch for latency spikes (may see temporary increase)
   - Note if any errors occur
   - Record metrics during failure (next 30-60 seconds)

5. **Check Admin UI**:
   - Node 3 should show as "Suspect" or "Dead"
   - Cluster should still be healthy (yellow warning is OK)

6. **Restart the failed node**:
   ```bash
   docker start roach3
   ```

7. **Monitor recovery**:
   - Watch metrics return to normal
   - Admin UI should show node 3 rejoining as "Live"

8. **Stop the load test** after 1-2 minutes of stable operation

### Expected Results:
- **During failure**: Slight latency increase, but no transaction failures
- **During recovery**: Metrics return to baseline
- **No data loss**: All transactions committed successfully

### What to Observe:
- **Automatic failover**: Remaining nodes handle traffic
- **Raft consensus**: Cluster maintains quorum (3 of 5 nodes)
- **Range re-replication**: CRDB replicas data from failed node
- **Leaseholder transfer**: Leadership moves to healthy nodes

---

## Data Collection & Analysis

For each test, record in a spreadsheet or document:

| Test | Nodes | TPS (avg) | p50 (ms) | p95 (ms) | p99 (ms) | Errors | Notes |
|------|-------|-----------|----------|----------|----------|--------|-------|
| Baseline | 3 | | | | | | |
| Scale-out (before) | 3 | | | | | | |
| Scale-out (after) | 5 | | | | | | |
| Index (before) | 5 | | | | | | |
| Index (during) | 5 | | | | | | |
| Index (after) | 5 | | | | | | |
| Node failure (baseline) | 5 | | | | | | |
| Node failure (during) | 4 | | | | | | |
| Node failure (recovered) | 5 | | | | | | |

## Key Findings to Highlight

When presenting your results, focus on:

1. **Scalability**:
   - How did TPS change when adding nodes?
   - Did latency improve or stay stable?
   - How long did rebalancing take?

2. **Online Operations**:
   - Could you add an index without stopping traffic?
   - What was the performance impact?
   - How does this compare to traditional databases?

3. **Fault Tolerance**:
   - Did any transactions fail when a node died?
   - How quickly did the cluster recover?
   - What would happen with 2 nodes down? (Not recommended to test - cluster would lose quorum)

4. **CRDB Core Concepts**:
   - **Ranges**: How data is split into ~64MB chunks
   - **Replicas**: Each range has 3 copies (by default)
   - **Leaseholders**: One replica per range handles reads/writes
   - **Raft consensus**: How nodes agree on data changes

## Cleanup

After all tests are complete:

```bash
# Stop all containers
docker-compose down

# Remove volumes (optional - deletes all data)
docker-compose down -v
```

## Troubleshooting

**Load test fails to connect:**
- Check cluster is running: `docker ps`
- Verify Admin UI is accessible at http://localhost:8080

**High latency or low TPS:**
- Check Docker Desktop resource limits (increase CPU/memory)
- Ensure no other heavy processes are running

**Node won't rejoin after failure:**
- Wait 1-2 minutes for Raft election
- Check docker logs: `docker logs roach3`

**Database setup fails:**
- Ensure cluster is initialized: `docker exec -it roach1 ./cockroach init --insecure`
- Try dropping and recreating: run `setup_database.py` again

---

## Quick Reference Commands

```bash
# Start 3-node cluster
docker-compose up -d roach1 roach2 roach3 && sleep 10 && docker exec -it roach1 ./cockroach init --insecure

# Add nodes 4 and 5
docker-compose up -d roach4 roach5

# Stop a node (simulate failure)
docker stop roach3

# Restart a node
docker start roach3

# View logs
docker logs roach1

# SQL shell
docker exec -it roach1 ./cockroach sql --insecure --database=study_db

# Check cluster status
docker exec -it roach1 ./cockroach node status --insecure
```

Good luck with your study! 🚀
