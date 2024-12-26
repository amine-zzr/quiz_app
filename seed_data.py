from app import create_app
from extensions import db
from models import Quiz, Question

def seed_database():
    app = create_app()
    with app.app_context():
        # Clear existing data
        Question.query.delete()
        Quiz.query.delete()
        db.session.commit()

        # Define quizzes with their questions
        quizzes = [
            {
                "title": "Python Basics",
                "description": "Test your knowledge of Python fundamentals",
                "time_limit": 10,
                "questions": [
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
            },
            {
                "title": "World History",
                "description": "Challenge your knowledge of major historical events",
                "time_limit": 15,
                "questions": [
                    {
                        "question_text": "In which year did World War II end?",
                        "option_a": "1943",
                        "option_b": "1944",
                        "option_c": "1945",
                        "option_d": "1946",
                        "correct_answer": "C"
                    },
                    {
                        "question_text": "Who was the first President of the United States?",
                        "option_a": "Thomas Jefferson",
                        "option_b": "John Adams",
                        "option_c": "Benjamin Franklin",
                        "option_d": "George Washington",
                        "correct_answer": "D"
                    },
                    {
                        "question_text": "Which ancient wonder was located in Alexandria?",
                        "option_a": "The Great Pyramid",
                        "option_b": "The Lighthouse",
                        "option_c": "The Hanging Gardens",
                        "option_d": "The Colossus",
                        "correct_answer": "B"
                    }
                ]
            },
            {
                "title": "Science Quiz",
                "description": "Test your knowledge of basic scientific concepts",
                "time_limit": 12,
                "questions": [
                    {
                        "question_text": "What is the chemical symbol for gold?",
                        "option_a": "Au",
                        "option_b": "Ag",
                        "option_c": "Fe",
                        "option_d": "Cu",
                        "correct_answer": "A"
                    },
                    {
                        "question_text": "Which planet is known as the Red Planet?",
                        "option_a": "Venus",
                        "option_b": "Jupiter",
                        "option_c": "Mars",
                        "option_d": "Saturn",
                        "correct_answer": "C"
                    },
                    {
                        "question_text": "What is the largest organ in the human body?",
                        "option_a": "Heart",
                        "option_b": "Brain",
                        "option_c": "Liver",
                        "option_d": "Skin",
                        "correct_answer": "D"
                    }
                ]
            },
            {
                "title": "Mathematics Challenge",
                "description": "Solve these mathematical problems",
                "time_limit": 20,
                "questions": [
                    {
                        "question_text": "What is the square root of 144?",
                        "option_a": "14",
                        "option_b": "12",
                        "option_c": "10",
                        "option_d": "16",
                        "correct_answer": "B"
                    },
                    {
                        "question_text": "What is 15% of 200?",
                        "option_a": "30",
                        "option_b": "25",
                        "option_c": "35",
                        "option_d": "40",
                        "correct_answer": "A"
                    },
                    {
                        "question_text": "If x + 5 = 12, what is x?",
                        "option_a": "5",
                        "option_b": "6",
                        "option_c": "7",
                        "option_d": "8",
                        "correct_answer": "C"
                    }
                ]
            },
            {
                "title": "General Knowledge",
                "description": "Test your knowledge across various topics",
                "time_limit": 15,
                "questions": [
                    {
                        "question_text": "Which is the largest ocean on Earth?",
                        "option_a": "Atlantic Ocean",
                        "option_b": "Indian Ocean",
                        "option_c": "Pacific Ocean",
                        "option_d": "Arctic Ocean",
                        "correct_answer": "C"
                    },
                    {
                        "question_text": "Who painted the Mona Lisa?",
                        "option_a": "Vincent van Gogh",
                        "option_b": "Leonardo da Vinci",
                        "option_c": "Pablo Picasso",
                        "option_d": "Michelangelo",
                        "correct_answer": "B"
                    },
                    {
                        "question_text": "What is the capital of Japan?",
                        "option_a": "Seoul",
                        "option_b": "Beijing",
                        "option_c": "Tokyo",
                        "option_d": "Bangkok",
                        "correct_answer": "C"
                    }
                ]
            }
        ]

        # Add quizzes and their questions to the database
        for quiz_data in quizzes:
            quiz = Quiz(
                title=quiz_data["title"],
                description=quiz_data["description"],
                time_limit=quiz_data["time_limit"]
            )
            db.session.add(quiz)
            db.session.commit()

            for q in quiz_data["questions"]:
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
    print("Database seeded successfully with multiple quizzes!")
