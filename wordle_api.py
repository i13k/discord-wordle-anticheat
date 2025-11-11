import aiohttp
import datetime

async def fetch_answer_from_api() -> dict:
    today_date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://www.nytimes.com/svc/wordle/v2/{today_date_str}.json") as r:
            if r.status == 200:
                return await r.json()
            raise Exception("Failed to fetch Wordle answer from API")

async def get_today_answer(answer_cache) -> str:
    if answer_cache["date"] == datetime.date.today():
        return answer_cache["word"]
    res = await fetch_answer_from_api()
    word = res.get("solution", "").lower()
    answer_cache["word"] = word
    answer_cache["date"] = datetime.date.today()
    return word
