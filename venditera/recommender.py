"""
==============================================================================
MODULE: recommender.py
PROJECT: Movie Recommendation System
DESCRIPTION: Content-based filtering with TF-IDF + cosine similarity.
             Operates entirely on the DataFrame produced by preprocessor.py
             (which is built from live TMDB API data).
==============================================================================
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings("ignore")


class MovieRecommender:
    """
    TF-IDF + Cosine Similarity content-based recommender.
    Trained on live TMDB data fetched via the API.
    """

    def __init__(self, max_features: int = 10_000):
        self._vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True,
        )
        self._sim_matrix = None
        self._df = None
        self._idx_map = {}

    def fit(self, df: pd.DataFrame) -> "MovieRecommender":
        self._df = df.reset_index(drop=True)
        tfidf = self._vectorizer.fit_transform(self._df["soup"].fillna(""))
        self._sim_matrix = linear_kernel(tfidf, tfidf)
        self._idx_map = {
            t.lower().strip(): i for i, t in enumerate(self._df["title"])
        }
        print(f"[Recommender] Ready — {len(self._df):,} movies indexed.")
        return self

    def _resolve(self, title: str) -> int | None:
        key = title.lower().strip()
        if key in self._idx_map:
            return self._idx_map[key]
        for k, i in self._idx_map.items():
            if key in k or k in key:
                return i
        return None

    def recommend(self, title: str, top_n: int = 10) -> pd.DataFrame:
        idx = self._resolve(title)
        if idx is None:
            return pd.DataFrame()

        sims = list(enumerate(self._sim_matrix[idx]))
        sims = sorted(sims, key=lambda x: x[1], reverse=True)
        sims = [s for s in sims if s[0] != idx]

        results = []
        for movie_idx, cos_sim in sims[: top_n * 3]:
            row = self._df.iloc[movie_idx]
            vote_norm = row["vote_average"] / 10.0
            score = 0.85 * cos_sim + 0.15 * vote_norm
            results.append({
                "title":        row["title"],
                "score":        round(score, 4),
                "vote_average": row["vote_average"],
                "genres":       row["genres"],
                "cast":         row["cast"],
                "director":     row["director"],
                "overview":     row["overview"],
                "release_date": row["release_date"],
                "poster_path":  row.get("poster_path", ""),
            })

        df_out = (
            pd.DataFrame(results)
            .sort_values("score", ascending=False)
            .head(top_n)
            .reset_index(drop=True)
        )
        df_out.index += 1
        return df_out

    def search(self, query: str, limit: int = 10) -> list[str]:
        q = query.lower().strip()
        return [
            self._df.iloc[i]["title"]
            for k, i in self._idx_map.items()
            if q in k
        ][:limit]

    @property
    def all_titles(self) -> list[str]:
        return self._df["title"].tolist() if self._df is not None else []
