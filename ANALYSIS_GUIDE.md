# CockroachDB Study - Analysis Guide

This guide helps you interpret test results and explain the distributed system behavior you observe.

## Key Metrics to Track

### 1. Throughput (TPS - Transactions Per Second)
- **What it means**: How many transactions the cluster completes per second
- **Good performance**: Higher is better (50-200+ TPS on local Docker)
- **What affects it**: Node count, network latency, resource contention

### 2. Latency (milliseconds)
- **p50 (median)**: Half of transactions complete faster than this
- **p95**: 95% of transactions complete faster than this
- **p99**: 99% of transactions complete faster than this (catches "tail latency")

**Good performance for local cluster:**
- p50: 5-20ms
- p95: 20-50ms
- p99: 30-100ms

**Why p99 matters**: Shows worst-case user experience. One slow transaction in 100 can hurt user perception.

---

## Test 1: Baseline Performance

### What You're Measuring
Establishing a performance baseline with 3 nodes.

### Key Observations

**✓ Expected behavior:**
- Stable TPS throughout the test
- Consistent low latency
- Zero errors

**🔍 What to look for in Admin UI:**
1. **Overview page**: All 3 nodes show "Live"
2. **Metrics → SQL Dashboard**: See query activity distributed across nodes
3. **Metrics → Replication**: Data spread across 3 nodes (each range has 3 replicas)

### Questions to Answer

1. **What is your baseline TPS?** _____________
2. **What is your p99 latency?** _____________
3. **How many ranges does your data span?** (Check Replication Dashboard) _____________

### Key Concept: Ranges
- CRDB splits data into 64MB chunks called "ranges"
- Each range is replicated 3 times (default)
- Your small test table likely fits in 1-2 ranges

---

## Test 2: Scale-Out (3 → 5 Nodes)

### What You're Measuring
How CRDB handles horizontal scaling during live traffic.

### Key Observations

**Phase 1: Before adding nodes (first 10-20 seconds)**
- Record baseline metrics

**Phase 2: Adding nodes (during `docker-compose up -d roach4 roach5`)**
- You might see a brief TPS dip or latency spike
- This is normal - cluster is discovering new nodes

**Phase 3: Rebalancing (next 2-3 minutes)**
- Cluster moves ranges to new nodes
- Watch "Replication Dashboard" in Admin UI

**Phase 4: Stabilized (after 3+ minutes)**
- TPS should return to normal or improve slightly
- Latency should be stable

**✓ Expected results:**
- TPS: Same or slightly higher (more nodes = more capacity)
- Latency: Similar or slightly better
- Data: Spread across all 5 nodes

### Questions to Answer

1. **TPS before scale-out:** _____________
2. **TPS after scale-out:** _____________
3. **Did you see any errors?** (Should be NO) _____________
4. **How long did rebalancing take?** (Approx. time) _____________

### Key Concepts

**Leaseholder:**
- One replica per range handles all reads/writes
- CRDB automatically balances leaseholders across nodes
- Adding nodes spreads leadership load

**Raft Consensus:**
- How replicas stay in sync
- Requires majority (quorum) to agree
- 3 of 5 nodes = cluster stays up even if 2 fail

### What This Demonstrates

- **Elastic scalability**: Add capacity without downtime
- **Automatic rebalancing**: No manual intervention needed
- **Zero data loss**: All transactions continue during migration

---

## Test 3: Online Schema Change (Add Index)

### What You're Measuring
Can you modify the schema while traffic continues?

### Key Observations

**Phase 1: Before index creation**
- Record baseline metrics

**Phase 2: During index creation (while running `CREATE INDEX`)**
- You'll likely see:
  - Latency increase (especially p95/p99)
  - Slight TPS decrease
  - This is expected - cluster is scanning table to build index

**Phase 3: After index completes**
- Metrics should return to normal
- Queries using the index may be faster

**✓ Expected results:**
- Temporary performance impact during index build
- No transaction failures
- System recovers after completion

### Questions to Answer

1. **p99 latency BEFORE index:** _____________
2. **p99 latency DURING index:** _____________
3. **p99 latency AFTER index:** _____________
4. **Any errors?** (Should be NO) _____________
5. **How long did index creation take?** _____________

### Key Concept: Online DDL

Traditional databases:
- Require maintenance window
- Lock table during schema change
- Cause downtime

CockroachDB:
- Changes schema online
- Uses backfill process (reads + writes index incrementally)
- Transactions never blocked

### What This Demonstrates

- **Zero-downtime operations**: No maintenance windows needed
- **Business continuity**: Users unaffected (except minor perf impact)
- **Operational flexibility**: Can evolve schema in production

---

## Test 4: Node Failure Simulation

### What You're Measuring
CRDB's fault tolerance and automatic recovery.

### Key Observations

**Phase 1: Baseline (first 10-20 seconds)**
- All 5 nodes healthy
- Normal performance

**Phase 2: Node failure (after `docker stop roach3`)**
- **Within 1-5 seconds:**
  - May see latency spike (as Raft detects failure)
  - TPS might dip briefly
  - Transactions continue (no failures!)

- **After 5-10 seconds:**
  - Cluster adapts
  - Ranges on failed node get new leaseholders
  - Performance returns to near-normal

**Phase 3: During failure (1-2 minutes)**
- Cluster running on 4 nodes
- Still has quorum (4 of 5 > 50%)
- Slightly degraded but functional

**Phase 4: Recovery (after `docker start roach3`)**
- Node rejoins cluster
- Catches up on missed writes
- Leaseholders rebalance

**✓ Expected results:**
- **Zero transaction failures** (this is critical!)
- Brief latency spike during failover
- Full recovery after node returns

### Questions to Answer

1. **p99 latency before failure:** _____________
2. **p99 latency during failure:** _____________
3. **p99 latency after recovery:** _____________
4. **Any transaction errors?** (Should be ZERO) _____________
5. **How long until performance normalized?** _____________

### Key Concepts

**Quorum:**
- CRDB needs majority of replicas to commit writes
- 5-node cluster: Can lose 2 nodes and still function
- Lost quorum = cluster unavailable (write-through safety)

**Automatic Failover:**
1. Node fails
2. Raft detects missing heartbeats (~1-3 seconds)
3. Remaining replicas elect new leaseholder
4. Cluster continues without human intervention

**Split-Brain Prevention:**
- Raft consensus prevents inconsistency
- Multiple nodes can't independently serve same range
- Ensures data integrity

### What This Demonstrates

- **High availability**: Cluster survives node failures
- **No data loss**: All committed transactions safe
- **Automatic recovery**: No operator intervention
- **Business continuity**: Users see brief latency blip, but no errors

---

## Summary: Key Findings to Present

When presenting your results, highlight these distributed systems principles:

### 1. **Horizontal Scalability**
- ✓ Added 2 nodes without downtime
- ✓ Data automatically rebalanced
- ✓ Performance scaled linearly (or stayed stable)

**Why it matters:** Traditional databases require vertical scaling (bigger servers). CRDB scales by adding commodity hardware.

### 2. **Operational Flexibility**
- ✓ Added index during live traffic
- ✓ No maintenance window needed
- ✓ Minor performance impact, no errors

**Why it matters:** Schema changes in production are risky in traditional databases. CRDB makes them safe.

### 3. **Fault Tolerance**
- ✓ Survived node failure with zero data loss
- ✓ Automatic failover in seconds
- ✓ Full recovery when node returned

**Why it matters:** Hardware fails. Networks partition. CRDB keeps applications running.

### 4. **Strong Consistency**
- ✓ Every read sees latest committed write
- ✓ No "eventual consistency" surprises
- ✓ ACID transactions across the cluster

**Why it matters:** Many distributed databases sacrifice consistency for availability (see: CAP theorem). CRDB gives you both.

---

## How CRDB Achieves This: Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   SQL Layer                              │
│  (Query parsing, optimization, transaction coordination) │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Distribution Layer                          │
│  • Ranges: Data split into ~64MB chunks                 │
│  • Replicas: Each range copied 3x across nodes          │
│  • Leaseholder: One replica handles reads/writes        │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│             Raft Consensus                               │
│  • Leader election                                       │
│  • Log replication                                       │
│  • Ensures all replicas agree                           │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Storage (RocksDB)                           │
│  • Persistent key-value store                           │
│  • MVCC (Multi-Version Concurrency Control)             │
└─────────────────────────────────────────────────────────┘
```

### Critical Path for a Write Transaction

1. **Client sends INSERT** → Connects to any node (gateway)
2. **Gateway finds leaseholder** → Uses routing table to find which node owns this range
3. **Leaseholder proposes to Raft** → "I want to append this write to the log"
4. **Raft replicates** → Sends to other 2 replicas
5. **Majority commits** → Once 2 of 3 replicas have it, safe to commit
6. **Client gets success** → Transaction completes

**Time**: ~10-20ms on your local cluster

### Why Latency Increases During Events

- **Scale-out**: Ranges moving = temporary unavailability, retry overhead
- **Index creation**: Extra reads to backfill index = resource contention
- **Node failure**: Raft leader election = brief pause, lease acquisition = retry

---

## Common Questions & Answers

**Q: Why didn't TPS double when I added 2 nodes?**

A: Your test table is small (few ranges). Adding nodes helps when you have many ranges to distribute. Also, your workload is serial (one Python script). Real applications have many concurrent clients.

**Q: Why do some transactions take 100ms+ (p99) when most take <10ms (p50)?**

A: "Tail latency" is common in distributed systems. Causes:
- Garbage collection pauses
- Network retries
- Disk I/O spikes
- Raft leadership changes

**Q: What happens if 3 nodes fail (lose quorum)?**

A: Cluster becomes unavailable for writes. Reads of stale data may succeed (depending on config). This is correct behavior - safety over availability.

**Q: Is CRDB AP or CP in the CAP theorem?**

A: **CP (Consistency + Partition tolerance)**. During a network partition, CRDB sacrifices availability to maintain consistency. This is the right choice for financial/mission-critical data.

---

## Final Checklist

Before presenting, ensure you can answer:

- ✓ What is a range? (Data chunk, ~64MB)
- ✓ What is a replica? (Copy of a range, 3 per range by default)
- ✓ What is a leaseholder? (Replica that handles reads/writes for a range)
- ✓ What is Raft? (Consensus algorithm that keeps replicas in sync)
- ✓ Why didn't transactions fail when a node died? (Raft quorum, 4 of 5 nodes still up)
- ✓ Why can CRDB add an index without downtime? (Online DDL, incremental backfill)
- ✓ How does CRDB scale? (Add nodes, data rebalances automatically)

Good luck with your presentation! 🎓
