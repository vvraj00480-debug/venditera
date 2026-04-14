"""
==============================================================================
MODULE: preprocessor.py
PROJECT: Movie Recommendation System
DESCRIPTION: Converts raw TMDB API movie dicts into a clean DataFrame
             ready for the recommendation engine. No CSV required.
==============================================================================
"""

import re
import pandas as pd


def _clean_token(name: str) -> str:
    """Remove spaces so multi-word tokens are treated as one by TF-IDF."""
    return name.replace(" ", "").lower()


def _clean_overview(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return re.sub(r"[^\w\s]", "", text.lower())


def build_dataframe(movies: list[dict]) -> pd.DataFrame:
    """
    Convert list of enriched movie dicts (from api_client) into a
    clean DataFrame with a 'soup' column for TF-IDF vectorisation.
    """
    rows = []
    for m in movies:
        if not m.get("title") or not m.get("overview"):
            continue

        genres_clean   = [_clean_token(g) for g in m.get("genres",   [])]
        keywords_clean = [_clean_token(k) for k in m.get("keywords", [])]
        cast_clean     = [_clean_token(c) for c in m.get("cast",     [])]
        director_clean = [_clean_token(m["director"])] if m.get("director") else []
        overview_clean = _clean_overview(m["overview"])

        # Soup: director gets 2x weight
        soup = " ".join(
            genres_clean
            + keywords_clean
            + cast_clean
            + director_clean * 2
            + overview_clean.split()
        )

        rows.append({
            "id":           m["id"],
            "title":        m["title"],
            "soup":         soup,
            "genres":       ", ".join(m.get("genres", [])),
            "cast":         ", ".join(m.get("cast", [])[:3]),
            "director":     m.get("director", ""),
            "overview":     m.get("overview", ""),
            "vote_average": float(m.get("vote_average", 0)),
            "vote_count":   int(m.get("vote_count", 0)),
            "release_date": str(m.get("release_date", ""))[:4],
            "popularity":   m.get("popularity", 0),
            "poster_path":  m.get("poster_path", ""),
        })

    df = pd.DataFrame(rows)
    df.drop_duplicates(subset="title", keep="first", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df
