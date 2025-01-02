# Quiz Application

A full-featured quiz application built with Flask that allows users to take timed multiple-choice quizzes and track their progress.

## Features

- User authentication and session management
- Multiple choice questions with time limits
- Score tracking and performance history
- RESTful API for quiz questions
- Responsive design for all devices

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
flask db upgrade
```

5. Run the application:
```bash
flask run
```

## Database Management

### Initial Setup
```bash
# Initialize migrations directory
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migrations
flask db upgrade
```

### Making Database Changes
1. Modify the models in `models.py`
2. Create a new migration:
```bash
flask db migrate -m "Description of changes"
```
3. Review the generated migration in `migrations/versions/`
4. Apply the migration:
```bash
flask db upgrade
```

### Common Database Operations
```bash
# View migration history
flask db history

# Rollback last migration
flask db downgrade

# Check current migration
flask db current

# Mark a migration as complete without running it
flask db stamp <migration_id>
```

### Troubleshooting
If you need to reset the database during development:
1. Delete the database file: `rm instance/quiz_app.db`
2. Delete migrations: `rm -rf migrations`
3. Reinitialize: 
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

**Warning**: Never reset the database in production. Always use migrations to make database changes.

## Project Structure

- `app.py`: Main application file
- `models.py`: Database models
- `api.py`: REST API endpoints
- `templates/`: HTML templates
- `static/`: CSS, JavaScript, and other static files
- `migrations/`: Database migrations
