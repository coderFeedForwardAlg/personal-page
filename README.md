# Docker Setup for Next.js and FastAPI Application

This repository contains Docker configuration for deploying a Next.js frontend and FastAPI backend application.

## Prerequisites

- Docker and Docker Compose installed on your system
- OpenAI API key for the backend

## Configuration

The application uses the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required for the backend)
- `NEXT_PUBLIC_API_URL`: The URL where the backend API is accessible (set automatically in docker-compose)

## Running the Application

1. **Set your OpenAI API key** in the `.env` file in the project root directory:

```
# .env file
OPENAI_API_KEY=your_actual_openai_api_key_here
```

Replace `your_actual_openai_api_key_here` with your actual OpenAI API key. This is required for the backend to function properly.

2. Build and start the containers:

```bash
docker-compose up -d
```

3. Access the applications:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Services

### Frontend (Next.js)

- Built with Next.js and Bun
- Communicates with the backend API
- Exposed on port 3000

### Backend (FastAPI)

- Built with FastAPI and Python
- Uses OpenAI API for AI responses
- Uses Chroma for vector storage
- Exposed on port 8000

## Volumes

- The Chroma database is persisted using a volume mount to ensure data is not lost between container restarts.

## Networks

- Both services are connected via a bridge network called `app-network`.

## Stopping the Application

To stop the application:

```bash
docker-compose down
```

## Development

For development purposes, you can run each service separately:

### Frontend

```bash
cd project-1747428226211
bun install
bun run dev
```

### Backend

```bash
cd backend
pip install -r req.txt
uvicorn chat:app --reload
```

### Generating the Vector Database

The backend uses a Chroma vector database to store and retrieve document embeddings. To generate or update this database:

1. Make sure your OpenAI API key is set in the `.env` file or as an environment variable
2. Place your markdown documents in the `backend/data/about` directory
3. Run the database generation script:

```bash
cd backend
python make_db.py
```

This will process all markdown files in the data directory, split them into chunks, generate embeddings using OpenAI, and store them in the Chroma database.