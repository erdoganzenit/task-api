# Task API with SQLite

A robust Task Management (CRUD) API built with FastAPI and SQLite, ensuring that data persists even after server restarts.

## Why SQLite?
- Requires no complex setup, configuration, or external database server (like PostgreSQL or MySQL).
- Lightweight and stores all data in a single local file.
- Perfect for rapid prototyping, development, and learning backend fundamentals.

## Where is the Database File Stored?
The database is automatically created and stored in the root directory of the project as `tasks.db`.

## How to Start the Project
1. Navigate to the project directory and install the required dependencies:
   ```bash
   
  pip install fastapi uvicorn pydantic
   

  Run the development server using Uvicorn:
  uvicorn main:app --reload

  Open your browser and navigate to the interactive API docs:


Example SQL Query

One of the core queries used to filter completed tasks in the database:
SELECT * FROM tasks WHERE done = 1;
