from flask_restful import Resource, Api
from flask import jsonify
from flask_login import current_user, login_required
from models import Quiz, UserQuizResult

def init_api(app):
    api = Api(app)

    class QuizListAPI(Resource):
        def get(self):
            quizzes = Quiz.query.all()
            return jsonify([{
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'time_limit': quiz.time_limit,
                'question_count': len(quiz.questions)
            } for quiz in quizzes])

    class QuizAPI(Resource):
        def get(self, quiz_id):
            quiz = Quiz.query.get_or_404(quiz_id)
            return jsonify({
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'time_limit': quiz.time_limit,
                'questions': [{
                    'id': q.id,
                    'question_text': q.question_text,
                    'options': {
                        'A': q.option_a,
                        'B': q.option_b,
                        'C': q.option_c,
                        'D': q.option_d
                    }
                } for q in quiz.questions]
            })

    class UserResultsAPI(Resource):
        @login_required
        def get(self):
            results = UserQuizResult.query.filter_by(user_id=current_user.id).all()
            return jsonify([{
                'quiz_id': result.quiz_id,
                'quiz_title': result.quiz.title,
                'score': result.score,
                'total_questions': result.total_questions,
                'percentage': (result.score / result.total_questions) * 100,
                'completed_at': result.completed_at.isoformat() if result.completed_at else None
            } for result in results])

    api.add_resource(QuizListAPI, '/api/quizzes')
    api.add_resource(QuizAPI, '/api/quizzes/<int:quiz_id>')
    api.add_resource(UserResultsAPI, '/api/results')
