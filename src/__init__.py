import requests
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()


class APIFootballClient:
    """Cliente para a API-Football v3."""

    BASE_URL = "https://v3.football.api-sports.io"

    def __init__(self, cache_dir: str = "data/cache"):
        self.api_key = os.getenv("API_FOOTBALL_KEY")
        if not self.api_key:
            raise ValueError("API Key não encontrada! Verifique o arquivo .env")
        self.headers = {
            "x-rapidapi-host": "v3.football.api-sports.io",
            "x-rapidapi-key": self.api_key,
        }
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get(self, endpoint: str, params: dict = None, use_cache: bool = True) -> dict:
        """Requisição GET com suporte a cache."""
        cache_key = endpoint.replace("/", "_")
        if params:
            cache_key += "_" + "_".join(f"{k}{v}" for k, v in sorted(params.items()))
        cache_file = self.cache_dir / f"{cache_key}.json"

        if use_cache and cache_file.exists():
            print(f"[CACHE] {endpoint}")
            with open(cache_file) as f:
                return json.load(f)

        print(f"[API]   GET /{endpoint} | params={params}")
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()

        if use_cache:
            with open(cache_file, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        time.sleep(0.5)  # respeita o rate limit
        return data

    def get_status(self) -> dict:
        """Verifica status e cota da conta."""
        return self._get("status", use_cache=False)

    def get_leagues(self, country: str = None, season: int = None) -> dict:
        params = {}
        if country: params["country"] = country
        if season:  params["season"] = season
        return self._get("leagues", params=params)

    def get_standings(self, league_id: int, season: int) -> dict:
        return self._get("standings", params={"league": league_id, "season": season})

    def get_fixtures(self, league_id: int, season: int, team_id: int = None) -> dict:
        params = {"league": league_id, "season": season}
        if team_id: params["team"] = team_id
        return self._get("fixtures", params=params)

    def get_teams(self, league_id: int, season: int) -> dict:
        return self._get("teams", params={"league": league_id, "season": season})

    def get_top_scorers(self, league_id: int, season: int) -> dict:
        return self._get("players/topscorers", params={"league": league_id, "season": season})

    def get_team_statistics(self, team_id: int, league_id: int, season: int) -> dict:
        return self._get("teams/statistics", params={"team": team_id, "league": league_id, "season": season})