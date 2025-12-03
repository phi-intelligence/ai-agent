# Core API

FastAPI backend for Phi Agents.

## Setup

1. Install dependencies:
   ```bash
   pip install poetry
   poetry install
   ```

2. Create `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and secret key
   ```

3. Run database migrations:
   ```bash
   alembic upgrade head
   ```

4. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at http://localhost:8000

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc


