# AI4ESG experiments

## Requirements:

Ensure you have the following installed:

- **Python**: Download and install from [python.org](https://www.python.org/downloads/). Currently, the project is using Python >=3.11, <3.12.
- Verify the python installation by running:
  ```sh
  python --version
  ```
- **Pip**: Install and upgrade to the latest version:
  ```sh
  python -m pip install --upgrade pip
  ```
- Verify the pip installation by running:
  ```sh
  pip --version
  ```
- **Poetry**: Install Poetry using pip:
  ```sh
  pip install poetry
  ```
- Verify the Poetry installation by running:
    ```sh
    poetry --version
    ```
- Docker and Docker Compose

### Installation

1. **Clone the Repository**
   ```sh
   git clone https://github.com/angelonti/ai4esg_experiments.git
   ```

2. **Install Dependencies**
   ```sh
   poetry install --without dev
   ```

3. **Activate the Virtual Environment**
   ```sh
   poetry self add poetry-plugin-shell
    ```
   ```sh
   poetry shell
   ```

## DB & Config

1. Run the SQL DB with `docker-compose up db -d`
2. run `cd backend`
3. Update database table structure: `poetry run alembic upgrade head`
4. Set your OpenAI API info in the .env file or in `backend\config.py`

## Run locally without Docker

```shell
python -m streamlit run frontend/app.py --server.port 8080
```

## Run locally with Docker

1. `docker build --progress=plain -t ai4esg-app:1.0 .`
2. `docker run -d -p 8080:8080 --name ai4esg-app ai4esg-app:1.0`