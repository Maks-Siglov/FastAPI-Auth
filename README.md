## Getting Started

1. Clone the Repository:
    ```bash
    git clone https://git.foxminded.ua/foxstudent105590/task_20_fastapi_auth.git
    cd task_20_fastapi_auth/
    ```

2. Create `fast_auth` postgres db.
    - **Example data in .env.docker:**
    ```bash
    DB_NAME=fast_auth
    DB_USER=admin
    DB_PASSWORD=admin
    DB_HOST=localhost
    DB_PORT=5432
    ```
## Start With Docker


1. Establish user

    ```bash
      source env.sh
     ```

2. Create docker network

    ```bash
      docker network create mynetwork  
     ```

3. Build app 
    ```bash
      docker compose build  
     ```

4. Start services 
    ```bash
      docker compose up  
     ```
   
5.  Visit `http://127.0.0.1:8080/`


## Run Locally

1. Install dependencies:

    ```bash
    pip install -r requirements/prod.txt -r requirements/tools.txt -r requirements/dev.txt
    ```

2. Apply migrations:

    ```bash
    python -m src.cli --upgrade
    ```

3. Run the development server:

    ```bash
    uvicorn src.app:app --host 0.0.0.0 --port 8000
    ```

4. Visit `http://127.0.0.1:8000/`
