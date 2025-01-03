from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import os
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect

from extensions import db, login_manager, migrate
from models import User, Quiz, Question, UserQuizResult
from api import init_api
from quiz_api import get_trivia_categories, fetch_and_save_quiz
from session_manager import (
    create_session, end_session, end_all_sessions,
    validate_session, get_user_sessions, cleanup_sessions,
    get_session_info
)

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///quiz.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # CSRF token doesn't expire

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf = CSRFProtect(app)  # Initialize CSRF protection
    init_api(app)

    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.before_request
    def before_request():
        if current_user.is_authenticated:
            if not validate_session():
                logout_user()
                flash('Your session has expired. Please login again.', 'warning')
                return redirect(url_for('login'))

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
            remember = request.form.get('remember', False) == 'on'
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                login_user(user, remember=remember)
                # Create new session
                create_session(user.id)
                
                next_page = request.args.get('next')
                flash('Login successful!', 'success')
                return redirect(next_page if next_page else url_for('dashboard'))
            else:
                flash('Invalid email or password', 'danger')
                return redirect(url_for('login'))
                
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            if not all([email, username, password, confirm_password]):
                flash('All fields are required')
                return redirect(url_for('register'))

            if password != confirm_password:
                flash('Passwords do not match')
                return redirect(url_for('register'))

            if User.query.filter_by(email=email).first():
                flash('Email already registered')
                return redirect(url_for('register'))

            if User.query.filter_by(username=username).first():
                flash('Username already taken')
                return redirect(url_for('register'))

            if not username.isalnum() or len(username) < 3 or len(username) > 20:
                flash('Username must be 3-20 characters long and contain only letters and numbers')
                return redirect(url_for('register'))

            user = User(
                email=email,
                username=username
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            login_user(user)
            return redirect(url_for('dashboard'))

        return render_template('register.html')

    @app.route('/logout')
    @login_required
    def logout():
        # End current session
        session_id = session.get('session_id')
        if session_id:
            end_session(session_id)
        
        # Clear the session
        session.clear()
        logout_user()
        flash('You have been logged out.', 'success')
        return redirect(url_for('login'))

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
        time_taken = data.get('time_taken', 0)  # Get time taken from request
        
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
        
        # Create and save the quiz result
        result = UserQuizResult(
            user_id=current_user.id,
            quiz_id=quiz_id,
            score=score,
            total_questions=total_questions,
            time_taken=time_taken,  # Save the time taken
            completed_at=datetime.utcnow()
        )
        
        db.session.add(result)
        db.session.commit()
        
        percentage = (score / total_questions) * 100
        return jsonify({
            'score': score,
            'total': total_questions,
            'percentage': percentage,
            'feedback': feedback,
            'time_taken': time_taken  # Return time taken in response
        })

    @app.route('/leaderboard')
    @login_required
    def leaderboard():
        # Get filter parameters
        quiz_id = request.args.get('quiz_id', type=int)
        timeframe = request.args.get('timeframe', 'all')

        # Base query to get the best score for each user
        results = db.session.query(
            UserQuizResult,
            User.username,
            Quiz.title,
            (UserQuizResult.score * 100.0 / UserQuizResult.total_questions).label('percentage')
        ).join(
            User, UserQuizResult.user_id == User.id
        ).join(
            Quiz, UserQuizResult.quiz_id == Quiz.id
        ).with_entities(
            User.id.label('user_id'),
            User.username,
            Quiz.title,
            func.max((UserQuizResult.score * 100.0 / UserQuizResult.total_questions)).label('best_percentage'),
            func.min(UserQuizResult.time_taken).label('best_time'),
            func.max(UserQuizResult.completed_at).label('latest_completion')
        ).group_by(
            User.id,
            User.username,
            Quiz.title
        )

        # Apply filters
        if quiz_id:
            results = results.filter(UserQuizResult.quiz_id == quiz_id)

        if timeframe != 'all':
            if timeframe == 'today':
                start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            elif timeframe == 'week':
                start_date = datetime.utcnow() - timedelta(days=7)
            elif timeframe == 'month':
                start_date = datetime.utcnow() - timedelta(days=30)
            results = results.filter(UserQuizResult.completed_at >= start_date)

        # Order by best percentage and best time
        results = results.order_by(
            desc('best_percentage'),
            'best_time'
        ).limit(100).all()

        # Calculate user stats
        user_results = UserQuizResult.query.filter_by(user_id=current_user.id).all()
        
        if user_results:
            total_quizzes = len(user_results)
            avg_score = sum(r.score * 100.0 / r.total_questions for r in user_results) / total_quizzes
            best_score = max(r.score * 100.0 / r.total_questions for r in user_results)
            
            # Calculate user's rank
            all_users_avg = db.session.query(
                UserQuizResult.user_id,
                func.avg(UserQuizResult.score * 100.0 / UserQuizResult.total_questions).label('avg_score')
            ).group_by(UserQuizResult.user_id).order_by(desc('avg_score')).all()
            
            try:
                user_rank = next(i for i, (user_id, _) in enumerate(all_users_avg, 1) if user_id == current_user.id)
            except StopIteration:
                user_rank = '-'
            
            user_stats = {
                'total_quizzes': total_quizzes,
                'avg_score': avg_score,
                'best_score': best_score,
                'rank': user_rank
            }
        else:
            user_stats = {
                'total_quizzes': 0,
                'avg_score': 0.0,
                'best_score': 0.0,
                'rank': '-'
            }

        return render_template('leaderboard.html',
                             leaderboard=results,
                             quizzes=Quiz.query.all(),
                             selected_quiz_id=quiz_id,
                             timeframe=timeframe,
                             user_stats=user_stats)

    @app.route('/account/sessions')
    @login_required
    def view_sessions():
        active_sessions = get_user_sessions(current_user.id)
        return render_template('sessions.html', sessions=active_sessions)

    @app.route('/account/sessions/end/<session_id>')
    @login_required
    def end_specific_session(session_id):
        session_info = get_session_info(session_id)
        if not session_info or session_info['user_id'] != current_user.id:
            flash('Invalid session.', 'danger')
            return redirect(url_for('view_sessions'))
        
        end_session(session_id)
        flash('Session ended successfully.', 'success')
        return redirect(url_for('view_sessions'))

    @app.route('/account/sessions/end-all')
    @login_required
    def end_all_user_sessions():
        current_session_id = session.get('session_id')
        end_all_sessions(current_user.id, except_session_id=current_session_id)
        flash('All other sessions have been ended.', 'success')
        return redirect(url_for('view_sessions'))

    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            # Check if username is taken
            if username != current_user.username:
                user_exists = User.query.filter_by(username=username).first()
                if user_exists:
                    flash('Username already taken.', 'danger')
                    return redirect(url_for('profile'))
            
            # Check if email is taken
            if email != current_user.email:
                email_exists = User.query.filter_by(email=email).first()
                if email_exists:
                    flash('Email already registered.', 'danger')
                    return redirect(url_for('profile'))
            
            # Update password if provided
            if new_password:
                if new_password != confirm_password:
                    flash('Passwords do not match.', 'danger')
                    return redirect(url_for('profile'))
                current_user.set_password(new_password)
            
            # Update user information
            current_user.username = username
            current_user.email = email
            db.session.commit()
            
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('profile'))
            
        return render_template('profile.html')

    # Run session cleanup periodically (24 hours)
    @app.cli.command('cleanup-sessions')
    def cleanup_sessions_command():
        """Cleanup expired sessions."""
        count = cleanup_sessions(max_age_hours=24)
        print(f'Cleaned up {count} expired sessions.')

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
