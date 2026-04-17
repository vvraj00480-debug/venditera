# """
# ==============================================================================
# MODULE: api_client.py
# PROJECT: Movie Recommendation System
# DESCRIPTION: TMDB API client — fetches live movie data (popular movies,
#              genres, cast, keywords, details) with local JSON caching.
#              No CSV download needed. Requires a free TMDB API key.

# GET YOUR FREE KEY: https://www.themoviedb.org/settings/api
# ==============================================================================
# """

import os
import json
import time
import requests

TMDB_BASE = "https://api.themoviedb.org/3"
CACHE_DIR  = os.path.join(os.environ.get("CACHE_DIR", "/tmp"), ".tmdb_cache")
CACHE_FILE = os.path.join(CACHE_DIR, "tmdb_movies.json")


# ---------------------------------------------------------------------------
# LOW-LEVEL REQUEST
# ---------------------------------------------------------------------------

def _get(endpoint: str, api_key: str, params: dict = None) -> dict:
    """Make a single TMDB API GET request."""
    url = f"{TMDB_BASE}/{endpoint}"
    p = {"api_key": api_key, "language": "en-US"}
    if params:
        p.update(params)
    r = requests.get(url, params=p, timeout=15)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# MOVIE FETCHING
# ---------------------------------------------------------------------------

def fetch_popular_movies(api_key: str, total_pages: int = 20) -> list[dict]:
    """
    Fetch popular movies from TMDB (20 movies per page).
    total_pages=20  →  ~400 movies  (fast, light)
    total_pages=50  →  ~1000 movies (richer recommendations)
    """
    movies = []
    for page in range(1, total_pages + 1):
        try:
            data = _get("movie/popular", api_key, {"page": page})
            movies.extend(data.get("results", []))
        except Exception as e:
            print(f"  [API] Page {page} failed: {e}")
        time.sleep(0.05)   # polite rate limiting
    return movies


def fetch_movie_details(movie_id: int, api_key: str) -> dict:
    """Fetch full details + credits + keywords in one call using append_to_response."""
    try:
        data = _get(
            f"movie/{movie_id}",
            api_key,
            {"append_to_response": "credits,keywords"},
        )
        return data
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# CACHE HELPERS
# ---------------------------------------------------------------------------

def _save_cache(data: list[dict]):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _load_cache() -> list[dict] | None:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def clear_cache():
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        print("[Cache] Cleared.")


# ---------------------------------------------------------------------------
# HIGH-LEVEL: BUILD ENRICHED MOVIE LIST
# ---------------------------------------------------------------------------

def build_movie_dataset(api_key: str, pages: int = 20, use_cache: bool = True) -> list[dict]:
    """
    Returns a list of enriched movie dicts ready for the recommender.
    Uses local cache to avoid re-fetching on every app restart.
    """
    if use_cache:
        cached = _load_cache()
        if cached:
            print(f"[API] Loaded {len(cached):,} movies from cache.")
            return cached

    print(f"[API] Fetching {pages * 20} popular movies from TMDB ...")
    popular = fetch_popular_movies(api_key, total_pages=pages)
    print(f"[API] Enriching with credits & keywords ({len(popular)} movies) ...")

    enriched = []
    for i, m in enumerate(popular, 1):
        details = fetch_movie_details(m["id"], api_key)
        if not details:
            continue

        # Cast (top 5)
        cast = [
            c["name"]
            for c in details.get("credits", {}).get("cast", [])[:5]
        ]

        # Director
        director = next(
            (c["name"] for c in details.get("credits", {}).get("crew", [])
             if c.get("job") == "Director"),
            "",
        )

        # Genres
        genres = [g["name"] for g in details.get("genres", [])]

        # Keywords
        keywords = [
            k["name"]
            for k in details.get("keywords", {}).get("keywords", [])[:10]
        ]

        enriched.append({
            "id":           details["id"],
            "title":        details.get("title", ""),
            "overview":     details.get("overview", ""),
            "genres":       genres,
            "cast":         cast,
            "director":     director,
            "keywords":     keywords,
            "vote_average": details.get("vote_average", 0),
            "vote_count":   details.get("vote_count", 0),
            "release_date": details.get("release_date", ""),
            "popularity":   details.get("popularity", 0),
            "poster_path":  details.get("poster_path", ""),
        })

        if i % 50 == 0:
            print(f"  ... enriched {i}/{len(popular)}")
        time.sleep(0.05)

    _save_cache(enriched)
    print(f"[API] Done. {len(enriched):,} movies saved to cache.")
    return enriched


def search_movie_online(query: str, api_key: str) -> list[dict]:
    """Search TMDB for a movie by name (for autocomplete / validation)."""
    try:
        data = _get("search/movie", api_key, {"query": query})
        return data.get("results", [])[:8]
    except Exception:
        return []
