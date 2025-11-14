import aiohttp
import datetime

async def fetch_answer_from_api() -> str:
    today_date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://www.nytimes.com/svc/wordle/v2/{today_date_str}.json") as r:
            if r.status == 200:
                return (await r.json()).get("solution", "")
            raise Exception("Failed to fetch Wordle answer from API")

async def update_answer_cache(answer_cache) -> tuple[datetime.date | None, str | None]:
    today = datetime.date.today()
    if answer_cache[0] == today:
        return answer_cache
    return (today, (await fetch_answer_from_api()))
