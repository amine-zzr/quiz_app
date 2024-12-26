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

## Project Structure

- `app.py`: Main application file
- `models.py`: Database models
- `api.py`: REST API endpoints
- `templates/`: HTML templates
- `static/`: CSS, JavaScript, and other static files
- `migrations/`: Database migrations
