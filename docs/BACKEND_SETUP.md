# Backend Setup

## Prerequisites

- Python 3.12+
- pip (Python package manager)
- Virtual environment support

## Step 1: Navigate to Backend Directory

```bash
cd backend
```

## Step 2: Create Virtual Environment

```bash
python3 -m venv .venv
```

This creates an isolated Python environment for the project.

## Step 3: Activate Virtual Environment

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

You should see `(.venv)` prefix in your terminal once activated.

## Step 4: Install Dependencies

Install all required Python packages from requirements.txt:

```bash
pip install -r requirements.txt
```

This installs:
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Motor** - Async MongoDB driver
- **Redis** - Caching/message broker
- **Celery** - Task queue
- **Playwright** - Browser automation for OCR
- **Pytest** - Testing framework
- **python-dotenv** - Environment variable management
- And other dependencies

## Step 5: Verify Installation

```bash
pip list
```

Confirm all packages are installed successfully.

## Step 6: Configure Environment Variables

Create a `.env` file in the `backend/` directory with the following:

```
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=grocery_intelligence
REDIS_URL=redis://localhost:6379
```

## Step 7: Start Docker Services (Optional but Recommended)

If you want to use MongoDB and Redis locally, start Docker Compose from the project root:

```bash
cd ..
docker-compose up -d
```

This starts MongoDB on port 27017 and Redis on port 6379.

### Verify Docker Services are Running

Check if containers are running:

```bash
docker-compose ps
```

Expected output shows `mongodb` and `redis` with status `Up`.

You can also check a single service:

```bash
docker-compose ps mongodb
docker-compose ps redis
```

### Verify MongoDB Connection

Test MongoDB is accessible:

```bash
# From backend directory
python3 -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017'); print('Connected to MongoDB:', client.admin.command('ping'))"
```

Or using MongoDB CLI (if installed):

```bash
mongosh "mongodb://localhost:27017"
```

If you are using Docker Compose, you can also confirm MongoDB is started by checking its container logs:

```bash
docker-compose logs mongodb
```

### Verify Redis Connection

Test Redis is accessible:

```bash
redis-cli ping
```

Expected response: `PONG`

### Stopping Docker Services

After each development session, stop the containers:

```bash
docker-compose down
```

This stops both MongoDB and Redis containers without removing data.

If you only want to stop MongoDB and keep Redis running:

```bash
docker-compose stop mongodb
```

### View Docker Logs

If you need to debug container issues:

```bash
# View logs for all services
docker-compose logs

# View logs for a specific service
docker-compose logs mongodb
docker-compose logs redis

# Follow logs in real-time
docker-compose logs -f mongodb
```

### Completely Remove Containers and Data

⚠️ **Warning:** This deletes all data. Only use if you want a fresh start:

```bash
docker-compose down -v
```

## Step 8: Run the Backend Server

```bash
uvicorn main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

You should see: **"Grocery Intelligence Platform API is running"**

## Step 9: Verify API is Working

Open your browser and visit:
```
http://localhost:8000/
```

You should receive the JSON response:
```json
{
  "message": "Grocery Intelligence Platform API is running"
}
```

## Step 10: Access API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

Both allow you to test endpoints directly in the browser.

## Troubleshooting

### Virtual environment not activating
- Make sure you're in the `backend/` directory
- Try: `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows)

### Port 8000 already in use
- Run on a different port: `uvicorn main:app --reload --port 8001`

### MongoDB/Redis connection errors
- Ensure Docker containers are running: `docker-compose up -d`
- Check `.env` has correct connection strings

### Module not found errors
- Verify virtual environment is activated (you should see `(.venv)` in terminal)
- Run `pip install -r requirements.txt` again

## Development Workflow

1. Activate virtual environment: `source .venv/bin/activate`
2. Start backend server: `uvicorn main:app --reload`
3. Make code changes (server auto-reloads)
4. Test endpoints via Swagger UI: `http://localhost:8000/docs`
5. Run tests: `pytest`
