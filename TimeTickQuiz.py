import requests
import html
import random
import threading
import time
import sys

CATEGORY_URL = "https://opentdb.com/api_category.php"
QUESTION_URL = "https://opentdb.com/api.php"
TIME_LIMIT = 15  # seconds per question

# Global game state
score = 0
question_count = 0
timer_expired = False
user_answer = None

# ------------------ API Functions ------------------

def fetch_categories():
    res = requests.get(CATEGORY_URL)
    if res.status_code == 200:
        categories = res.json()["trivia_categories"]
        return {cat["id"]: cat["name"] for cat in categories}
    return {}

def fetch_questions(category=None, difficulty=None, qtype=None):
    url = QUESTION_URL + "?amount=1"
    if category:
        url += f"&category={category}"
    if difficulty:
        url += f"&difficulty={difficulty}"
    if qtype:
        url += f"&type={qtype}"

    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        if data["response_code"] == 0:
            return data["results"][0]
    return None

# ------------------ User Input Selection ------------------

def select_category(categories):
    print("\n📚 Categories:")
    for cid, name in categories.items():
        print(f"{cid}: {name}")
    while True:
        choice = input("Choose category ID: ")
        if choice.isdigit() and int(choice) in categories:
            return int(choice)
        print("❌ Invalid category ID.")

def select_difficulty():
    levels = ["easy", "medium", "hard"]
    while True:
        level = input("Choose difficulty (easy/medium/hard): ").lower()
        if level in levels:
            return level
        print("❌ Invalid difficulty.")

def select_question_type():
    types = ["multiple", "boolean"]
    while True:
        qtype = input("Choose question type (multiple/boolean): ").lower()
        if qtype in types:
            return qtype
        print("❌ Invalid type.")

# ------------------ Quiz Logic ------------------

def countdown_timer():
    global timer_expired
    for t in range(TIME_LIMIT, 0, -1):
        sys.stdout.write(f"\r⏱️  Time left: {t} seconds ")
        sys.stdout.flush()
        time.sleep(1)
    timer_expired = True
    print("\n⏰ Time's up!")

def ask_question(category_id, difficulty, q_type):
    global score, question_count, timer_expired, user_answer
    q = fetch_questions(category_id, difficulty, q_type)
    if not q:
        print("⚠️ Failed to fetch question.")
        return

    question_count += 1
    print(f"\nQ{question_count}: {html.unescape(q['question'])}")

    options = q['incorrect_answers'] + [q['correct_answer']]
    options = [html.unescape(opt) for opt in options]
    if q['type'] == 'multiple':
        random.shuffle(options)

    correct = html.unescape(q['correct_answer'])

    for i, opt in enumerate(options, 1):
        print(f"{i}. {opt}")

    # Start timer
    timer_expired = False
    timer_thread = threading.Thread(target=countdown_timer)
    timer_thread.start()

    try:
        user_answer = input("\nYour answer (1/2/3/4): ")
    except:
        user_answer = None

    if not timer_expired:
        timer_thread.join()
        try:
            selected = int(user_answer)
            if options[selected - 1] == correct:
                print("✅ Correct!")
                score += 1
            else:
                print(f"❌ Incorrect. Correct answer: {correct}")
        except:
            print("⚠️ Invalid input.")
    else:
        print(f"⏳ You ran out of time! Correct answer was: {correct}")

def select_quiz_options(categories):
    cat = select_category(categories)
    diff = select_difficulty()
    qtype = select_question_type()

    while True:
        try:
            num = int(input("How many questions? (1–20): "))
            if 1 <= num <= 20:
                break
        except:
            pass
        print("❌ Invalid number.")
    return cat, diff, qtype, num

# ------------------ Main Function ------------------

def main():
    print("🎮 Welcome to TimeTickQuiz - A Battle Against the Clock!")

    categories = fetch_categories()
    if not categories:
        print("❌ Could not load categories. Exiting.")
        return

    category_id, difficulty, q_type, num_questions = select_quiz_options(categories)

    for _ in range(num_questions):
        ask_question(category_id, difficulty, q_type)

    print(f"\n🏁 Game Over! Final Score: {score}/{question_count}")
    print("🎉 Thanks for playing TimeTickQuiz!")

if __name__ == "__main__":
    main()

