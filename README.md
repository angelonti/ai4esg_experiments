# AI4ESG experiments

## Usage

1. Install Docker and Docker Compose
2. Run the SQL DB with `docker-compose up db -d`
3. Install poetry with `pip install poetry`
4. run `cd backend`
5. Create a virtual environment with `poetry shell`
6. Install dependencies with `poetry install --no-root`
7. Update database table structure: `poetry run alembic upgrade head`
8. Set your OpenAI API info in the .env file or in `backend\config.py`
9. Now you can run the cells in the notebook `experimets/AI4ESG_experiments.ipynb`

## Run locally

1. docker build --progress=plain -t ai4esg-app:1.0 . 
2. docker run -d -p 8080:8080 --name ai4esg-app ai4esg-app:1.0