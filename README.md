# QuizMaster - Interactive Learning Platform

QuizMaster is a modern, feature-rich quiz application built with Flask that allows users to create, take, and share quizzes. It supports both custom quiz creation and automatic quiz generation using external APIs.

## 🌟 Features

### User Management
- 🔐 Secure user authentication with password hashing
- 👤 User profiles with customizable settings
- 📊 Personal statistics and quiz history
- 🔑 Session management with multi-device support

### Quiz Features
- 📝 Create custom quizzes with multiple-choice questions
- 🎲 Generate quizzes automatically from a vast question bank
- ⏱️ Timed quiz sessions
- 📈 Detailed feedback and explanations
- 🏆 Global leaderboard with filtering options

### Security
- 🛡️ CSRF protection for all forms
- 🔒 Secure session handling
- 🔐 Password strength requirements
- ⚡ Protection against common web vulnerabilities

### UI/UX
- 📱 Responsive design for all devices
- 🎨 Modern and intuitive interface
- ⚡ Real-time feedback and animations
- 🌓 Clean and professional styling

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/amine-zzr/quiz_app.git
cd quiz_app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
flask db upgrade
python seed_data.py  # Optional: Add sample data
```

6. Run the application:
```bash
flask run
```

The application will be available at `http://localhost:5000`

## 🏗️ Project Structure

```
quiz_app/
├── app.py              # Main application file
├── api.py             # API routes and handlers
├── extensions.py      # Flask extensions
├── models.py          # Database models
├── quiz_api.py        # External quiz API integration
├── session_manager.py # Session handling
├── requirements.txt   # Project dependencies
├── .env.example      # Example environment variables
├── static/           # Static files (CSS, JS, images)
│   ├── css/         # Stylesheets
│   └── js/          # JavaScript files
├── templates/        # HTML templates
│   ├── base.html    # Base template
│   ├── index.html   # Landing page
│   └── ...          # Other templates
└── migrations/      # Database migrations
```

## 🔧 Configuration

The application can be configured using environment variables in the `.env` file:

- `SECRET_KEY`: Flask secret key for session security
- `DATABASE_URL`: Database connection URL
- `QUIZ_API_KEY`: External quiz API key (optional)
- `SESSION_LIFETIME`: Session duration in minutes
- `MAX_SESSIONS`: Maximum concurrent sessions per user

## 🛠️ Development

### Database Migrations

To make database changes:
```bash
flask db migrate -m "Description of changes"
flask db upgrade
```


## 📚 API Documentation

### External Quiz API Integration
The application integrates with external quiz APIs to generate questions:

- Supports multiple categories
- Configurable difficulty levels
- Custom amount of questions per quiz

### Internal API Endpoints
- `/api/quizzes`: List all quizzes
- `/api/quiz/<id>`: Get specific quiz
- `/api/submit`: Submit quiz answers
- `/api/leaderboard`: Get leaderboard data

## 🔐 Security Considerations

- All passwords are hashed using bcrypt
- CSRF protection on all forms
- Session management with secure token handling
- Input validation and sanitization
- Rate limiting on sensitive endpoints

## 🚀 Deployment

This application is configured for deployment on [Render.com](https://render.com).

### Quick Deploy Steps

1. Push your code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/amine-zzr/quiz_app.git
git push -u origin main
```

2. On Render.com:
   - Sign up for a free account
   - Create a new Web Service
   - Connect your GitHub repository
   - Use the following settings:
     - Name: quizmaster
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn wsgi:app`

3. The application will be available at your Render URL

### Note
- Free tier may sleep after 15 minutes of inactivity
- First request after inactivity may take ~30 seconds

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 🙏 Acknowledgments

- Flask and its extensions
- Bootstrap for UI components
- Open Trivia Database API
- All contributors and users

## 📧 Contact

For questions and support, please open an issue or contact [aminezoukri@gmail.com].

---
Made with ❤️ by amine-zzr
