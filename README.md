# AI4ESG experiments

## Usage

1. Install poetry with `pip install poetry`
2. Create a virtual environment with `poetry shell`
3. Install dependencies with `poetry install -C .\backend\ --no-root`
4. Install Docker and Docker Compose
5. Run the SQL DB with `docker-compose up db -d`.
6. Update database table structure: `poetry run alembic upgrade head`.
7. Now you can run the cells in the notebook `experimets/AI4ESG_experiments.ipynb`