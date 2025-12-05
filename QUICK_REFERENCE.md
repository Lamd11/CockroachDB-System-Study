# Quick Reference - CockroachDB Study

## 🚀 Quick Start Commands

```bash
# 1. Start cluster (run once)
docker-compose up -d roach1 roach2 roach3 && sleep 10 && docker exec -it roach1 ./cockroach init --insecure

# 2. Setup database (run once)
python scripts/setup_database.py

# 3. Check everything is working
python scripts/check_cluster.py

# 4. Run load test (60 seconds, report every 10 seconds)
python scripts/load_test.py 60 10
```

## 📊 Test Scenarios

### Test 1: Baseline (3 nodes)
```bash
python scripts/load_test.py 60 10
```
Record: TPS, p50, p95, p99

### Test 2: Scale-out (3 → 5 nodes)
```bash
# Terminal 1: Start continuous load
python scripts/load_test.py

# Terminal 2: Add nodes
docker-compose up -d roach4 roach5
```
Record: TPS/latency before and after

### Test 3: Online index creation
```bash
# Terminal 1: Start continuous load
python scripts/load_test.py

# Terminal 2: Add index
python scripts/add_index.py
```
Record: TPS/latency before, during, after

### Test 4: Node failure
```bash
# Terminal 1: Start continuous load
python scripts/load_test.py

# Terminal 2: Kill and restart node
docker stop roach3
sleep 30
docker start roach3
```
Record: TPS/latency during failure and recovery

## 🌐 Admin UI

Open in browser: http://localhost:8080

**Key pages:**
- Overview: Node health
- Metrics → SQL Dashboard: Query activity
- Metrics → Replication: Range distribution

## 📁 Files Created

### Scripts
- `scripts/setup_database.py` - Initialize DB and table
- `scripts/load_test.py` - Main load testing script with metrics
- `scripts/check_cluster.py` - Health check utility
- `scripts/add_index.py` - Helper for online schema change test

### Documentation
- `TEST_INSTRUCTIONS.md` - Detailed step-by-step test procedures
- `ANALYSIS_GUIDE.md` - How to interpret results and explain findings
- `QUICK_REFERENCE.md` - This file

## 🔧 Troubleshooting

**Cluster won't start:**
```bash
docker-compose down -v
docker-compose up -d roach1 roach2 roach3
sleep 10
docker exec -it roach1 ./cockroach init --insecure
```

**Load test can't connect:**
```bash
python scripts/check_cluster.py
```

**Reset everything:**
```bash
docker-compose down -v
# Then run quick start commands again
```

## 📊 Metrics Cheat Sheet

**Good Performance (local cluster):**
- TPS: 50-200+
- p50: 5-20ms
- p95: 20-50ms
- p99: 30-100ms
- Errors: 0

**What affects performance:**
- Number of nodes (more = better for large datasets)
- Docker resource limits (increase if needed)
- Other processes competing for CPU/disk

## 🎓 Key Concepts

| Concept | Definition |
|---------|-----------|
| **Range** | 64MB chunk of data |
| **Replica** | Copy of a range (3 by default) |
| **Leaseholder** | Replica that handles reads/writes |
| **Raft** | Consensus algorithm for replication |
| **Quorum** | Majority of replicas (2 of 3, or 3 of 5) |

## 📝 Data Collection Template

| Test | Nodes | TPS | p50 | p95 | p99 | Errors | Notes |
|------|-------|-----|-----|-----|-----|--------|-------|
| Baseline | 3 | | | | | | |
| Scale-out (before) | 3 | | | | | | |
| Scale-out (after) | 5 | | | | | | |
| Index (before) | 5 | | | | | | |
| Index (during) | 5 | | | | | | |
| Index (after) | 5 | | | | | | |
| Failure (baseline) | 5 | | | | | | |
| Failure (during) | 4 | | | | | | |
| Failure (recovered) | 5 | | | | | | |

## 🧹 Cleanup

```bash
# Stop containers (keep data)
docker-compose down

# Stop and delete all data
docker-compose down -v

# Exit Python environment
deactivate
```
