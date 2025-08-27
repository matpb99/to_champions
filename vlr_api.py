import asyncio
import aiohttp
import pandas as pd

API_URL = "https://vlrggapi.vercel.app/match"


async def fetch_page(session, page):
    params = {"q": "results", "from_page": page, "to_page": page}
    try:
        await asyncio.sleep(0.1)
        async with session.get(API_URL, params=params) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientResponseError:
        return None
    except aiohttp.ClientConnectorError:
        return None
    except Exception:
        return None


def parse_matches_from_data(data, page):
    if not data or "data" not in data or "segments" not in data["data"]:
        # Log the error, but don't print to stdout
        return []

    segments = data["data"]["segments"]
    if not segments:
        return []

    found_matches = []
    for match in segments:
        tournament_name = match.get("tournament_name", "")
        if (
            "americas" in tournament_name.lower()
            and "stage 2" in tournament_name.lower()
        ):
            team1_name = match.get("team1")
            team2_name = match.get("team2")
            score1_str = match.get("score1")
            score2_str = match.get("score2")

            if not all([team1_name, team2_name, score1_str, score2_str]):
                continue

            score1 = int(score1_str)
            score2 = int(score2_str)
            winner = team1_name if score1 > score2 else team2_name
            loser = team2_name if score1 > score2 else team1_name

            found_matches.append(
                {
                    "team1": team1_name,
                    "team2": team2_name,
                    "winner": winner,
                    "loser": loser,
                    "score": f"{score1}-{score2}",
                    "maps": [],
                }
            )
    return found_matches


async def get_played_matches_async(total_pages_to_check=10):
    all_played_matches = []

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_page(session, page) for page in range(1, total_pages_to_check + 1)
        ]
        results = await asyncio.gather(*tasks)

        for i, data in enumerate(results):
            page_num = i + 1
            if data:
                matches = parse_matches_from_data(data, page_num)
                all_played_matches.extend(matches)

    return all_played_matches


def load_played_matches():
    if pd.compat.is_platform_windows():
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    return asyncio.run(get_played_matches_async())
