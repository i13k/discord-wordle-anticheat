import requests
import datetime

def fetch_answer_from_api() -> dict:
    today_date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    r = requests.get(f"https://www.nytimes.com/svc/wordle/v2/{today_date_str}.json")
    if r.status_code == 200:
        return r.json()
    raise Exception("Failed to fetch Wordle answer from API")

def get_today_answer(answer_cache) -> str:
    if answer_cache["date"] == datetime.date.today():
        return answer_cache["word"]
    word = fetch_answer_from_api().get("solution", "").lower()
    answer_cache["word"] = word
    answer_cache["date"] = datetime.date.today()
    return word
