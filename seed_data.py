from app import create_app
from extensions import db
from models import Quiz, Question

def seed_database():
    app = create_app()
    with app.app_context():
        # Create a sample quiz
        quiz = Quiz(
            title="Python Basics",
            description="Test your knowledge of Python fundamentals",
            time_limit=10  # 10 minutes
        )
        db.session.add(quiz)
        db.session.commit()

        # Add questions to the quiz
        questions = [
            {
                "question_text": "What is Python?",
                "option_a": "A snake",
                "option_b": "A programming language",
                "option_c": "A web browser",
                "option_d": "An operating system",
                "correct_answer": "B"
            },
            {
                "question_text": "Which of these is a valid Python comment?",
                "option_a": "// Comment",
                "option_b": "/* Comment */",
                "option_c": "# Comment",
                "option_d": "<!-- Comment -->",
                "correct_answer": "C"
            },
            {
                "question_text": "What is the output of print(2 + 3)?",
                "option_a": "23",
                "option_b": "5",
                "option_c": "2 + 3",
                "option_d": "Error",
                "correct_answer": "B"
            }
        ]

        for q in questions:
            question = Question(
                quiz_id=quiz.id,
                question_text=q["question_text"],
                option_a=q["option_a"],
                option_b=q["option_b"],
                option_c=q["option_c"],
                option_d=q["option_d"],
                correct_answer=q["correct_answer"]
            )
            db.session.add(question)
        
        db.session.commit()

if __name__ == "__main__":
    seed_database()
    print("Database seeded successfully!")
