# Tweeza

Tweeza is a community service platform that connects organizations, volunteers, and beneficiaries to coordinate charity and community service activities.

## Features

- User registration and authentication
- Organization management
- Event planning and coordination
- Resource requests and contributions management
- Beneficiary tracking

## Project Structure

- `frontend/`: Next.js web application
- `backend/`: FastAPI backend service

## Getting Started

### Backend

1. Change to the backend directory:

   ```bash
   cd backend
   ```
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:

   ```bash
   uvicorn app.main:app --reload
   ```
4. Access the API documentation at http://localhost:8000/api/docs

### Frontend

1. Change to the frontend directory:

   ```bash
   cd frontend
   ```
2. Install dependencies:

   ```bash
   npm install
   ```
3. Run the development server:

   ```bash
   npm run dev
   ```
4. Access the web application at http://localhost:3000

## Docker Deployment

Use Docker Compose to run the entire application:

```bash
docker-compose up -d
```
