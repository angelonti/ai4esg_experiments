# AI4ESG experiments

## Usage

1. Install poetry with `pip install poetry`
2. run `cd backend`
3. Create a virtual environment with `poetry shell`
4. Install dependencies with `poetry install --no-root`
5. Install Docker and Docker Compose
6. Run the SQL DB with `docker-compose up db -d`
7. Update database table structure: `poetry run alembic upgrade head`
8. Set your OpenAI API key in `backend\config.py`
9. Now you can run the cells in the notebook `experimets/AI4ESG_experiments.ipynb`