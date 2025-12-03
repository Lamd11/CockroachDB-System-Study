# CockroachDB-System-Study
This project is a case study of CockroachDB’s distributed behavior. We will build a 3-node cluster with Docker, run a Python script that constantly writes/reads data, then test what happens when we add nodes, add an index, or kill a node.



Before running the project, ensure you have the following installed on your machine:
 - Docker Desktop (Must be running)
 - Python 3.10+ 


Setting up the work study: 

    1. Create the Virtual Environment

       ```python3 -m venv venv```

    2. Activate the Environment

        Linux:
        ```source venv/bin/activate```

        Windows (PowerShell):
        .\venv\Scripts\activate

    3. Install Dependencies

        ```pip install -r requirements.txt```






Put this in browser for CockroachDB AdminUI after cluster is live:
http://localhost:8080



To close python enviroment:
    ```deactivate```