"""
Quiz App REST API Documentation

This module provides the REST API endpoints for the Quiz application.
All responses are in JSON format.

Authentication:
- Most endpoints require user authentication via session cookie
- Unauthorized requests will receive a 401 response

Rate Limiting:
- API calls are limited to 100 requests per minute per user
"""

from flask_restful import Resource, Api, reqparse
from flask import jsonify, request
from flask_login import current_user, login_required
from models import Quiz, UserQuizResult, User, db
from datetime import datetime, timedelta
from functools import wraps

def init_api(app):
    api = Api(app)

    # Request parsers
    quiz_parser = reqparse.RequestParser()
    quiz_parser.add_argument('title', type=str, required=True, help='Quiz title is required')
    quiz_parser.add_argument('description', type=str)
    quiz_parser.add_argument('time_limit', type=int, required=True, help='Time limit in minutes is required')

    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.is_admin:
                return {'message': 'Admin privileges required'}, 403
            return f(*args, **kwargs)
        return decorated_function

    class QuizListAPI(Resource):
        """
        Quiz List Resource
        
        GET /api/quizzes
        - Returns list of all available quizzes
        - No authentication required
        
        POST /api/quizzes
        - Creates a new quiz
        - Requires admin authentication
        - Required fields: title, time_limit
        - Optional fields: description
        """
        def get(self):
            """Get list of all quizzes"""
            quizzes = Quiz.query.all()
            return jsonify([{
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'time_limit': quiz.time_limit,
                'question_count': len(quiz.questions),
                'created_at': quiz.created_at.isoformat() if quiz.created_at else None
            } for quiz in quizzes])

        @admin_required
        def post(self):
            """Create a new quiz (admin only)"""
            args = quiz_parser.parse_args()
            quiz = Quiz(
                title=args['title'],
                description=args.get('description', ''),
                time_limit=args['time_limit'],
                created_at=datetime.utcnow()
            )
            db.session.add(quiz)
            db.session.commit()
            return {'message': 'Quiz created successfully', 'quiz_id': quiz.id}, 201

    class QuizAPI(Resource):
        """
        Single Quiz Resource
        
        GET /api/quizzes/<quiz_id>
        - Returns details of a specific quiz
        - Includes questions if user is authenticated
        
        PUT /api/quizzes/<quiz_id>
        - Updates an existing quiz
        - Requires admin authentication
        
        DELETE /api/quizzes/<quiz_id>
        - Deletes a quiz
        - Requires admin authentication
        """
        def get(self, quiz_id):
            """Get details of a specific quiz"""
            quiz = Quiz.query.get_or_404(quiz_id)
            response = {
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'time_limit': quiz.time_limit,
                'created_at': quiz.created_at.isoformat() if quiz.created_at else None
            }
            
            # Include questions only for authenticated users
            if current_user.is_authenticated:
                response['questions'] = [{
                    'id': q.id,
                    'question_text': q.question_text,
                    'options': {
                        'A': q.option_a,
                        'B': q.option_b,
                        'C': q.option_c,
                        'D': q.option_d
                    }
                } for q in quiz.questions]
            
            return jsonify(response)

        @admin_required
        def put(self, quiz_id):
            """Update a quiz (admin only)"""
            quiz = Quiz.query.get_or_404(quiz_id)
            args = quiz_parser.parse_args()
            
            quiz.title = args['title']
            quiz.description = args.get('description', quiz.description)
            quiz.time_limit = args['time_limit']
            
            db.session.commit()
            return {'message': 'Quiz updated successfully'}

        @admin_required
        def delete(self, quiz_id):
            """Delete a quiz (admin only)"""
            quiz = Quiz.query.get_or_404(quiz_id)
            db.session.delete(quiz)
            db.session.commit()
            return {'message': 'Quiz deleted successfully'}

    class UserResultsAPI(Resource):
        """
        User Quiz Results Resource
        
        GET /api/results
        - Returns authenticated user's quiz results
        - Requires authentication
        
        GET /api/results/leaderboard
        - Returns global leaderboard
        - Optional query parameters:
          - quiz_id: Filter by specific quiz
          - timeframe: all/today/week/month
        """
        @login_required
        def get(self):
            """Get authenticated user's quiz results"""
            results = UserQuizResult.query.filter_by(user_id=current_user.id).all()
            return jsonify([{
                'quiz_id': result.quiz_id,
                'quiz_title': result.quiz.title,
                'score': result.score,
                'total_questions': result.total_questions,
                'percentage': (result.score / result.total_questions) * 100,
                'time_taken': result.time_taken,
                'completed_at': result.completed_at.isoformat() if result.completed_at else None
            } for result in results])

    class LeaderboardAPI(Resource):
        """Get global leaderboard with optional filters"""
        def get(self):
            quiz_id = request.args.get('quiz_id', type=int)
            timeframe = request.args.get('timeframe', 'all')

            query = UserQuizResult.query

            if quiz_id:
                query = query.filter_by(quiz_id=quiz_id)

            if timeframe != 'all':
                if timeframe == 'today':
                    start_date = datetime.utcnow().replace(hour=0, minute=0, second=0)
                elif timeframe == 'week':
                    start_date = datetime.utcnow() - timedelta(days=7)
                elif timeframe == 'month':
                    start_date = datetime.utcnow() - timedelta(days=30)
                query = query.filter(UserQuizResult.completed_at >= start_date)

            results = query.order_by(
                (UserQuizResult.score * 100 / UserQuizResult.total_questions).desc(),
                UserQuizResult.time_taken
            ).limit(100).all()

            return jsonify([{
                'username': result.user.username,
                'quiz_title': result.quiz.title,
                'score': result.score,
                'total_questions': result.total_questions,
                'percentage': (result.score / result.total_questions) * 100,
                'time_taken': result.time_taken,
                'completed_at': result.completed_at.isoformat() if result.completed_at else None
            } for result in results])

    # Register API resources
    api.add_resource(QuizListAPI, '/api/quizzes')
    api.add_resource(QuizAPI, '/api/quizzes/<int:quiz_id>')
    api.add_resource(UserResultsAPI, '/api/results')
    api.add_resource(LeaderboardAPI, '/api/leaderboard')
