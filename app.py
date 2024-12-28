from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, desc
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
                title = request.form.get('title')
                description = request.form.get('description')
                time_limit = int(request.form.get('time_limit'))
                
                quiz = Quiz(
                    title=title,
                    description=description,
                    time_limit=time_limit,
                    created_by=current_user.id
                )
                db.session.add(quiz)
                db.session.flush()  # Get the quiz ID
                
                # Process questions
                question_count = len(request.form.getlist('questions[][text]'))
                for i in range(question_count):
                    question = Question(
                        quiz_id=quiz.id,
                        question_text=request.form.getlist('questions[][text]')[i],
                        option_a=request.form.getlist('questions[][option_a]')[i],
                        option_b=request.form.getlist('questions[][option_b]')[i],
                        option_c=request.form.getlist('questions[][option_c]')[i],
                        option_d=request.form.getlist('questions[][option_d]')[i],
                        correct_answer=request.form.getlist('questions[][correct_answer]')[i],
                        explanation=request.form.getlist('questions[][explanation]')[i]
                    )
                    db.session.add(question)
                
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
        data = request.get_json()
        answers = data.get('answers', {})
        time_taken = data.get('time_taken', 0)
        
        score = 0
        total_questions = len(quiz.questions)
        feedback = []
        
        for question_id, answer in answers.items():
            question = Question.query.get(int(question_id))
            if question:
                is_correct = question.correct_answer == answer
                if is_correct:
                    score += 1
                
                feedback.append({
                    'question_id': question.id,
                    'is_correct': is_correct,
                    'correct_answer': question.correct_answer,
                    'explanation': question.explanation,
                    'your_answer': answer
                })
        
        result = UserQuizResult(
            user_id=current_user.id,
            quiz_id=quiz_id,
            score=score,
            total_questions=total_questions,
            time_taken=time_taken,
            completed_at=datetime.utcnow()
        )
        
        db.session.add(result)
        db.session.commit()
        
        percentage = (score / total_questions) * 100
        return jsonify({
            'score': score,
            'total': total_questions,
            'percentage': percentage,
            'feedback': feedback
        })

    @app.route('/leaderboard')
    @login_required
    def leaderboard():
        # Get filter parameters
        quiz_id = request.args.get('quiz_id', type=int)
        timeframe = request.args.get('timeframe', 'all')

        # Base query
        query = db.session.query(UserQuizResult).\
            join(Quiz).\
            join(User)

        # Apply filters
        if quiz_id:
            query = query.filter(UserQuizResult.quiz_id == quiz_id)

        if timeframe != 'all':
            if timeframe == 'today':
                start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            elif timeframe == 'week':
                start_date = datetime.utcnow() - timedelta(days=7)
            elif timeframe == 'month':
                start_date = datetime.utcnow() - timedelta(days=30)
            query = query.filter(UserQuizResult.completed_at >= start_date)

        # Get results ordered by score percentage and time taken
        leaderboard = query.order_by(
            desc((UserQuizResult.score * 100 / UserQuizResult.total_questions)),
            UserQuizResult.time_taken
        ).limit(100).all()

        # Calculate user stats
        user_stats = {}
        user_results = UserQuizResult.query.filter_by(user_id=current_user.id).all()
        if user_results:
            total_quizzes = len(user_results)
            avg_score = sum(r.score * 100 / r.total_questions for r in user_results) / total_quizzes
            best_score = max(r.score * 100 / r.total_questions for r in user_results)
            
            # Calculate user's rank
            all_users_avg = db.session.query(
                UserQuizResult.user_id,
                func.avg(UserQuizResult.score * 100 / UserQuizResult.total_questions).label('avg_score')
            ).group_by(UserQuizResult.user_id).order_by(desc('avg_score')).all()
            
            user_rank = next(i for i, (user_id, _) in enumerate(all_users_avg, 1) if user_id == current_user.id)
            
            user_stats = {
                'total_quizzes': total_quizzes,
                'avg_score': avg_score,
                'best_score': best_score,
                'rank': user_rank
            }
        else:
            user_stats = {
                'total_quizzes': 0,
                'avg_score': 0,
                'best_score': 0,
                'rank': '-'
            }

        return render_template('leaderboard.html',
                             leaderboard=leaderboard,
                             quizzes=Quiz.query.all(),
                             selected_quiz_id=quiz_id,
                             timeframe=timeframe,
                             user_stats=user_stats)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
