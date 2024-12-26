import requests
import html
from models import Quiz, Question
from extensions import db

TRIVIA_API_URL = "https://opentdb.com/api.php"
CATEGORY_API_URL = "https://opentdb.com/api_category.php"

def get_trivia_categories():
    """Fetch available quiz categories from the API"""
    try:
        response = requests.get(CATEGORY_API_URL)
        response.raise_for_status()
        return response.json()['trivia_categories']
    except requests.RequestException as e:
        print(f"Error fetching categories: {e}")
        return []

def fetch_and_save_quiz(category_id=None, difficulty=None, amount=10):
    """
    Fetch questions from the API and save as a new quiz
    
    Args:
        category_id (int): Optional category ID
        difficulty (str): Optional difficulty level ('easy', 'medium', 'hard')
        amount (int): Number of questions to fetch (default: 10)
    """
    params = {
        'amount': amount,
        'type': 'multiple'  # We only want multiple choice questions
    }
    
    if category_id:
        params['category'] = category_id
    if difficulty:
        params['difficulty'] = difficulty

    try:
        response = requests.get(TRIVIA_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data['response_code'] != 0:
            raise ValueError("Failed to fetch questions from API")

        # Create a new quiz
        category_name = get_category_name(category_id) if category_id else "Mixed"
        difficulty_text = f" ({difficulty.capitalize()})" if difficulty else ""
        quiz = Quiz(
            title=f"{category_name} Quiz{difficulty_text}",
            description=f"Test your knowledge in {category_name}!",
            time_limit=15  # 15 minutes default time limit
        )
        db.session.add(quiz)
        db.session.commit()

        # Add questions to the quiz
        for q_data in data['results']:
            # Create a list of all answers and shuffle them
            options = [html.unescape(q_data['correct_answer'])] + [
                html.unescape(ans) for ans in q_data['incorrect_answers']
            ]
            
            # Map the correct answer to A, B, C, or D
            correct_index = 0  # Index of correct answer is always 0 before shuffling
            correct_letter = chr(65 + correct_index)  # Convert 0 to 'A', 1 to 'B', etc.

            question = Question(
                quiz_id=quiz.id,
                question_text=html.unescape(q_data['question']),
                option_a=options[0],
                option_b=options[1],
                option_c=options[2],
                option_d=options[3],
                correct_answer=correct_letter
            )
            db.session.add(question)

        db.session.commit()
        return quiz

    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching quiz: {e}")
        db.session.rollback()
        return None

def get_category_name(category_id):
    """Get category name from category ID"""
    categories = get_trivia_categories()
    for category in categories:
        if category['id'] == category_id:
            return category['name']
    return "General Knowledge"
