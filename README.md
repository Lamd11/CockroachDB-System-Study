# CockroachDB-System-Study
This project is a case study of CockroachDB's distributed behavior. We will build a 3-node cluster with Docker, run a Python script that constantly writes/reads data, then test what happens when we add nodes, add an index, or kill a node.

## Prerequisites

Before running the project, ensure you have the following installed on your machine:
 - Docker Desktop (Must be running)
 - Python 3.10+

## Setup

1. **Create the Virtual Environment**
   ```bash
   python3 -m venv venv
   ```

2. **Activate the Environment**
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     .\venv\Scripts\activate
     ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

1. **Start the 3-node cluster:**
   ```bash
   docker-compose up -d roach1 roach2 roach3
   sleep 10
   docker exec -it roach1 ./cockroach init --insecure
   ```

2. **Initialize the database:**
   ```bash
   python scripts/setup_database.py
   ```

3. **Verify cluster health:**
   ```bash
   python scripts/check_cluster.py
   ```

4. **Run a load test:**
   ```bash
   python scripts/load_test.py 60 10
   ```

For complete testing instructions, see [TEST_INSTRUCTIONS.md](TEST_INSTRUCTIONS.md)






## Available Scripts

- `scripts/setup_database.py` - Initialize database and schema
- `scripts/load_test.py [duration] [interval]` - Run load test with metrics
- `scripts/check_cluster.py` - Verify cluster health
- `scripts/add_index.py` - Add index during load testing
- `scripts/test.py` - Original connection test

## Admin UI

View the CockroachDB Admin UI at:
```
http://localhost:8080
```

## Cleanup

```bash
# Stop all containers
docker-compose down

# Remove all data volumes
docker-compose down -v

# Deactivate Python environment
deactivate
```