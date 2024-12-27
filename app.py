from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from extensions import db, login_manager, migrate
from models import User, Quiz, Question, UserQuizResult
from api import init_api
from quiz_api import get_trivia_categories, fetch_and_save_quiz

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///quiz.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    init_api(app)

    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password_hash, password):
                login_user(user, remember=True)
                next_page = request.args.get('next')
                flash('Login successful!', 'success')
                return redirect(next_page if next_page else url_for('dashboard'))
            flash('Invalid email or password', 'danger')
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            # Validate email format
            if not email or '@' not in email:
                flash('Please enter a valid email address', 'danger')
                return redirect(url_for('register'))
            
            # Check if email already exists
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'danger')
                return redirect(url_for('register'))
            
            # Validate password
            if not password or len(password) < 8:
                flash('Password must be at least 8 characters long', 'danger')
                return redirect(url_for('register'))
            
            if not any(c.isupper() for c in password):
                flash('Password must contain at least one uppercase letter', 'danger')
                return redirect(url_for('register'))
                
            if not any(c.islower() for c in password):
                flash('Password must contain at least one lowercase letter', 'danger')
                return redirect(url_for('register'))
                
            if not any(c.isdigit() for c in password):
                flash('Password must contain at least one number', 'danger')
                return redirect(url_for('register'))
                
            if not any(c in '!@#$%^&*(),.?":{}|<>' for c in password):
                flash('Password must contain at least one special character', 'danger')
                return redirect(url_for('register'))
            
            # Check if passwords match
            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return redirect(url_for('register'))
            
            # Create new user
            user = User(email=email, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            flash('Registration successful!', 'success')
            return redirect(url_for('dashboard'))
            
        return render_template('register.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out successfully', 'info')
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Get user's quizzes (ones they created)
        user_created_quizzes = Quiz.query.filter_by(created_by=current_user.id).all()
        
        # Get all available quizzes
        all_quizzes = Quiz.query.all()
        
        # Get user's quiz results
        results = UserQuizResult.query.filter_by(user_id=current_user.id).all()
        
        # Get quiz categories from the API
        try:
            categories = get_trivia_categories()
        except:
            categories = []  # Fallback if API call fails
            
        return render_template('dashboard.html', 
                             user_quizzes=user_created_quizzes,
                             quizzes=all_quizzes, 
                             results=results, 
                             categories=categories)

    @app.route('/create_quiz', methods=['GET', 'POST'])
    @login_required
    def create_quiz():
        if request.method == 'POST':
            try:
                # Get quiz details
                title = request.form.get('title')
                description = request.form.get('description')
                time_limit = int(request.form.get('time_limit'))

                # Create new quiz
                quiz = Quiz(
                    title=title,
                    description=description,
                    time_limit=time_limit,
                    created_by=current_user.id
                )
                db.session.add(quiz)
                db.session.flush()  # Get the quiz ID before committing

                # Process questions
                questions_data = []
                i = 0
                while f'questions[{i}][text]' in request.form:
                    question_text = request.form.get(f'questions[{i}][text]')
                    correct_answer = request.form.get(f'questions[{i}][correct]')
                    
                    # Get options
                    options = {
                        'A': request.form.get(f'questions[{i}][options][A]'),
                        'B': request.form.get(f'questions[{i}][options][B]'),
                        'C': request.form.get(f'questions[{i}][options][C]'),
                        'D': request.form.get(f'questions[{i}][options][D]')
                    }
                    
                    question = Question(
                        quiz_id=quiz.id,
                        question_text=question_text,
                        option_a=options['A'],
                        option_b=options['B'],
                        option_c=options['C'],
                        option_d=options['D'],
                        correct_answer=correct_answer
                    )
                    questions_data.append(question)
                    i += 1

                # Add all questions
                db.session.bulk_save_objects(questions_data)
                db.session.commit()

                flash('Quiz created successfully!', 'success')
                return redirect(url_for('dashboard'))

            except Exception as e:
                db.session.rollback()
                flash('Error creating quiz. Please try again.', 'danger')
                print(f"Error creating quiz: {str(e)}")
                return redirect(url_for('create_quiz'))

        return render_template('create_quiz.html')

    @app.route('/create_quiz_api', methods=['POST'])
    @login_required
    def create_quiz_api():
        category_id = request.form.get('category_id')
        difficulty = request.form.get('difficulty')
        
        if category_id:
            category_id = int(category_id)
        
        quiz = fetch_and_save_quiz(
            category_id=category_id,
            difficulty=difficulty,
            amount=10  # 10 questions per quiz
        )
        
        if quiz:
            flash('New quiz created successfully!', 'success')
            return redirect(url_for('take_quiz', quiz_id=quiz.id))
        else:
            flash('Failed to create quiz. Please try again.', 'danger')
            return redirect(url_for('dashboard'))

    @app.route('/quiz/<int:quiz_id>')
    @login_required
    def take_quiz(quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        return render_template('quiz.html', quiz=quiz)

    @app.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
    @login_required
    def submit_quiz(quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        answers = request.get_json()
        
        score = 0
        total_questions = len(quiz.questions)
        
        for question_id, answer in answers.items():
            question = Question.query.get(int(question_id))
            if question and question.correct_answer == answer:
                score += 1
        
        result = UserQuizResult(
            user_id=current_user.id,
            quiz_id=quiz_id,
            score=score,
            total_questions=total_questions,
            completed_at=datetime.utcnow()
        )
        
        db.session.add(result)
        db.session.commit()
        
        percentage = (score / total_questions) * 100
        return jsonify({
            'score': score,
            'total': total_questions,
            'percentage': percentage
        })

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
