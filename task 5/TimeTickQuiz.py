import requests
import html
import random
import threading
import time
import sys

CATEGORIES_API = "https://opentdb.com/api_category.php"
QUESTIONS_API = "https://opentdb.com/api.php"
TIME_PER_QUESTION = 15  

total_score = 0
total_questions = 0
time_up = False
player_choice = None


def get_categories():
    response = requests.get(CATEGORIES_API)
    if response.status_code == 200:
        data = response.json()["trivia_categories"]
        return {c["id"]: c["name"] for c in data}
    return {}


def get_question(category=None, difficulty=None, q_format=None):
    url = QUESTIONS_API + "?amount=1"
    if category:
        url += f"&category={category}"
    if difficulty:
        url += f"&difficulty={difficulty}"
    if q_format:
        url += f"&type={q_format}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["response_code"] == 0:
            return data["results"][0]
    return None


def choose_category(categories):
    print("\nAvailable Categories:")
    for cid, name in categories.items():
        print(f"{cid}: {name}")
    while True:
        choice = input("Enter category ID: ")
        if choice.isdigit() and int(choice) in categories:
            return int(choice)
        print("Invalid category ID, try again.")


def choose_difficulty():
    levels = ["easy", "medium", "hard"]
    while True:
        level = input("Choose difficulty (easy/medium/hard): ").lower()
        if level in levels:
            return level
        print("Invalid choice.")


def choose_question_type():
    types = ["multiple", "boolean"]
    while True:
        q_format = input("Choose question type (multiple/boolean): ").lower()
        if q_format in types:
            return q_format
        print("Invalid choice.")


def start_timer():
    global time_up
    for remaining in range(TIME_PER_QUESTION, 0, -1):
        sys.stdout.write(f"\rTime left: {remaining} seconds ")
        sys.stdout.flush()
        time.sleep(1)
    time_up = True
    print("\nTime’s up!")


def present_question(category_id, difficulty, q_format):
    global total_score, total_questions, time_up, player_choice
    question_data = get_question(category_id, difficulty, q_format)
    if not question_data:
        print("Could not fetch a question.")
        return

    total_questions += 1
    print(f"\nQ{total_questions}: {html.unescape(question_data['question'])}")

    choices = question_data['incorrect_answers'] + [question_data['correct_answer']]
    choices = [html.unescape(opt) for opt in choices]

    if question_data['type'] == 'multiple':
        random.shuffle(choices)

    correct_answer = html.unescape(question_data['correct_answer'])

    for idx, opt in enumerate(choices, 1):
        print(f"{idx}. {opt}")

    # Timer thread
    time_up = False
    timer_thread = threading.Thread(target=start_timer)
    timer_thread.start()

    try:
        player_choice = input("\nYour answer (1/2/3/4): ")
    except:
        player_choice = None

    if not time_up:
        timer_thread.join()
        try:
            selected_index = int(player_choice)
            if choices[selected_index - 1] == correct_answer:
                print("Correct!")
                total_score += 1
            else:
                print(f"Wrong! The correct answer was: {correct_answer}")
        except:
            print("Invalid input.")
    else:
        print(f"You ran out of time! Correct answer was: {correct_answer}")


def set_quiz_options(categories):
    cat = choose_category(categories)
    diff = choose_difficulty()
    q_format = choose_question_type()

    while True:
        try:
            num = int(input("How many questions would you like? (1–20): "))
            if 1 <= num <= 20:
                break
        except:
            pass
        print("Invalid number.")
    return cat, diff, q_format, num


def main():
    print("Welcome to TimeTickQuiz - Beat the Clock!")

    categories = get_categories()
    if not categories:
        print("Could not load categories.")
        return

    category_id, difficulty, q_format, num_questions = set_quiz_options(categories)

    for _ in range(num_questions):
        present_question(category_id, difficulty, q_format)

    print(f"\nGame Over! Your Final Score: {total_score}/{total_questions}")


if __name__ == "__main__":
    main()
