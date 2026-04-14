"""
==============================================================================
MODULE: demo.py
PROJECT: Movie Recommendation System
DESCRIPTION: Command-line demo — run the recommender without Streamlit.
             Useful for testing, CI pipelines, or notebook exploration.

USAGE:
    python demo.py
    python demo.py --movie "Inception" --top 5 --engine hybrid
==============================================================================
"""

import argparse
import textwrap
import time

from preprocessor import preprocess
from recommender import ContentBasedRecommender, HybridRecommender


# ─── ANSI colour helpers ──────────────────────────────────────────────────────
GOLD   = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
DIM    = "\033[2m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def print_header():
    print(f"\n{GOLD}{'═'*60}{RESET}")
    print(f"{BOLD}{GOLD}  🎬  CineMatch — Movie Recommendation System{RESET}")
    print(f"{GOLD}{'═'*60}{RESET}\n")


def print_results(recs, query: str, elapsed: float):
    score_col = "score" if "score" in recs.columns else (
                "cb_score" if "cb_score" in recs.columns else None)

    print(f"\n{CYAN}  Recommendations for → {BOLD}{query}{RESET}")
    print(f"  {DIM}({elapsed*1000:.0f} ms){RESET}\n")
    print(f"  {'#':<4} {'Title':<40} {'Score':>6}  {'Rating':>6}  Genres")
    print(f"  {'─'*80}")

    for rank, (_, row) in enumerate(recs.iterrows(), 1):
        score = row.get(score_col, 0) if score_col else 0
        title = str(row["title"])[:38]
        rating = row.get("vote_average", 0)
        genres = str(row.get("genres", ""))[:30]
        bar_len = int(score * 20)
        bar = f"{GOLD}{'█' * bar_len}{DIM}{'░' * (20 - bar_len)}{RESET}"
        print(f"  {rank:<4} {title:<40} {score:>5.3f}  {rating:>5.1f}   {genres}")

    print(f"\n  {DIM}{'─'*80}{RESET}")


def interactive_mode(engine, df):
    print_header()
    print(f"  {DIM}Dataset loaded: {len(df):,} movies{RESET}")
    print(f"  Type a movie name to get recommendations (or 'q' to quit)\n")

    while True:
        try:
            query = input(f"  {GOLD}→  Movie: {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if query.lower() in ("q", "quit", "exit"):
            break
        if not query:
            continue

        # Fuzzy search hint
        matches = engine.search_titles(query, limit=5)
        if matches and matches[0].lower() != query.lower():
            print(f"\n  {DIM}Did you mean: {', '.join(matches[:3])}?{RESET}")

        t0 = time.time()
        recs = engine.recommend(query, top_n=10)
        elapsed = time.time() - t0

        if recs.empty:
            print(f"\n  {RED}  ✗  Movie not found. Try: {matches[:3]}{RESET}\n")
        else:
            print_results(recs, query, elapsed)


def batch_mode(engine, movie: str, top_n: int):
    print_header()
    t0 = time.time()
    recs = engine.recommend(movie, top_n=top_n)
    elapsed = time.time() - t0
    if recs.empty:
        print(f"  {RED}✗ Movie '{movie}' not found in dataset.{RESET}")
    else:
        print_results(recs, movie, elapsed)
        # Also print full overview for top result
        top = recs.iloc[0]
        print(f"\n  {BOLD}Top Pick → {top['title']}{RESET}")
        overview = str(top.get("overview", ""))
        for line in textwrap.wrap(overview, width=70):
            print(f"    {DIM}{line}{RESET}")
        print()


# ─── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CineMatch CLI demo")
    parser.add_argument("--movie",  type=str, default=None,
                        help="Movie title to query (interactive mode if omitted)")
    parser.add_argument("--top",    type=int, default=10,
                        help="Number of recommendations (default: 10)")
    parser.add_argument("--engine", type=str, default="content",
                        choices=["content", "hybrid"],
                        help="Recommendation engine to use")
    args = parser.parse_args()

    print("\n  Loading dataset and fitting model …")
    df = preprocess()

    if args.engine == "hybrid":
        from recommender import HybridRecommender
        engine = HybridRecommender(alpha=0.7).fit(df)
    else:
        engine = ContentBasedRecommender().fit(df)

    if args.movie:
        batch_mode(engine, args.movie, args.top)
    else:
        interactive_mode(engine, df)
