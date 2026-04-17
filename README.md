# 🎬 CineMatch — Movie Recommendation System

> *An intelligent, content-aware movie recommendation engine built with Python, Scikit-learn, and Streamlit.*

---

## 📋 Table of Contents

1. [Objective](#1-objective)  
2. [Problem Statement](#2-problem-statement)  
3. [Methodology](#3-methodology)  
4. [Architecture & Modules](#4-architecture--modules)  
5. [Dataset](#5-dataset)  
6. [Algorithms](#6-algorithms)  
7. [Setup & Installation](#7-setup--installation)  
8. [Usage](#8-usage)  
9. [Output & Results](#9-output--results)  
10. [Future Scope](#10-future-scope)  
11. [References](#11-references)

---

## 1. Objective

Design and implement a **movie recommendation system** that:

- Provides accurate, personalised movie recommendations based on a user-selected title.  
- Uses **content-based filtering** (TF-IDF + cosine similarity) as the primary engine.  
- Optionally blends **collaborative filtering** (item-based CF) for improved accuracy.  
- Exposes a clean, production-quality **web interface** via Streamlit.  
- Downloads and caches the TMDB 5000 dataset automatically at first launch.

---

## 2. Problem Statement

The modern streaming landscape contains tens of thousands of titles. Users experience **choice paralysis** and frequently cannot discover movies aligned with their tastes. A well-designed recommendation system solves this by:

| Challenge | Solution |
|-----------|----------|
| Cold-start (new user) | Content-based filtering needs no user history |
| High-dimensional feature space | TF-IDF reduces noise; cosine sim handles sparsity |
| Scalability | Vectorised NumPy operations, cached similarity matrix |
| Explainability | Feature breakdown (genre, cast, director) per card |

---

## 3. Methodology

```
Raw Data (TMDB CSV)
       │
       ▼
┌─────────────────────────────┐
│  preprocessor.py            │
│  ─ Merge movies + credits   │
│  ─ Extract genres, keywords │
│  ─ Extract cast, director   │
│  ─ Clean overview text      │
│  ─ Build 'soup' string      │
└────────────┬────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
Content-Based     Collaborative
  Engine            Engine
(TF-IDF +        (Item-based CF
 cosine sim)      synthetic UIM)
    │                 │
    └────────┬────────┘
             │
             ▼
        Hybrid Score
    α·CB + (1-α)·CF
             │
             ▼
      Streamlit UI
   (ranked movie cards)
```

### 3.1 Feature Engineering

| Feature | Extraction | Processing |
|---------|-----------|------------|
| Genres | JSON parse | Cleaned, joined, deduplicated |
| Keywords | JSON parse | Stemmed, cleaned |
| Cast | JSON parse (top-5) | Actor names as tokens |
| Director | JSON crew filter | 2× weight (repeated token) |
| Overview | Raw text | Lowercased, punctuation stripped |

### 3.2 Vectorisation

All features are concatenated into a **soup string** and fed to `TfidfVectorizer`:

```
soup = genre_tokens + keyword_tokens + cast_tokens + director(×2) + overview_words
```

TF-IDF parameters:
- `max_features = 15,000`
- `ngram_range = (1, 2)` — captures bi-gram phrases (e.g. "action thriller")
- `sublinear_tf = True` — logarithmic TF scaling
- `stop_words = "english"`

### 3.3 Similarity Computation

```
similarity(A, B) = cos(θ) = (A · B) / (‖A‖ · ‖B‖)
```

A full **N × N cosine similarity matrix** is pre-computed and cached in memory.  
`sklearn.metrics.pairwise.linear_kernel` is used for speed (equivalent to cosine for L2-normalised TF-IDF vectors).

### 3.4 Hybrid Scoring

```
score_hybrid = α · score_CB  +  (1-α) · score_CF
```

Default α = 0.7 (70% content-based, 30% collaborative).

---

## 4. Architecture & Modules

```
movie_recommendation_system/
│
├── app.py              ← Streamlit web application (UI layer)
├── recommender.py      ← Core engines (CB + CF + Hybrid)
├── preprocessor.py     ← Data loading, cleaning, feature extraction
├── requirements.txt    ← Python dependencies
├── README.md           ← Project documentation (this file)
│
└── .cache/             ← Auto-created; stores downloaded CSVs
    ├── movies.csv
    └── credits.csv
```

### Module Responsibilities

#### `preprocessor.py`

| Function | Responsibility |
|----------|---------------|
| `load_raw_data()` | Downloads / reads TMDB CSVs with local caching |
| `_extract_genres()` | Parses JSON genre lists → clean token list |
| `_extract_cast()` | Parses JSON cast lists → top-N actor tokens |
| `_extract_director()` | Filters crew JSON for Director role |
| `_clean_overview()` | Strips punctuation, lowercases text |
| `preprocess()` | Full pipeline → returns cleaned DataFrame |

#### `recommender.py`

| Class | Method | Responsibility |
|-------|--------|---------------|
| `ContentBasedRecommender` | `fit(df)` | Builds TF-IDF + similarity matrix |
| | `recommend(title, top_n)` | Returns ranked DataFrame |
| | `search_titles(query)` | Fuzzy title search |
| `CollaborativeRecommender` | `fit(df)` | Synthesises user-item matrix + item similarity |
| | `recommend(title, top_n)` | CF-based recommendations |
| `HybridRecommender` | `fit(df)` | Fits both engines |
| | `recommend(title, top_n)` | Weighted hybrid results |

#### `app.py`

- Streamlit page config, CSS theming (cinematic dark mode)  
- `load_model()` — `@st.cache_resource` for zero-reload after first run  
- Selectbox for movie selection (full title list)  
- Two-column card layout with match-score progress bars  
- CSV download of results  
- Bar chart of similarity scores

---

## 5. Dataset

**TMDB 5000 Movie Dataset**

| Property | Value |
|----------|-------|
| Source | [TMDB / Kaggle](https://www.kaggle.com/tmdb/tmdb-movie-metadata) |
| Size | ~4,800 movies |
| Columns used | `title, genres, keywords, cast, crew, overview, vote_average, vote_count, release_date` |
| Auto-download | Yes — via GitHub raw URL on first launch |
| Local cache | `.cache/movies.csv`, `.cache/credits.csv` |

---

## 6. Algorithms

### Content-Based Filtering

**Pros:** Works without any user history; highly explainable.  
**Cons:** Limited to item similarity; "filter bubble" effect over time.

### Collaborative Filtering (Item-Based)

**Pros:** Captures latent patterns across user preferences.  
**Cons:** Requires rating data; cold-start problem for new items.

### Hybrid Model

Combines both paradigms. The weighted blend balances the strengths of each approach and is tunable via the α slider.

---

## 7. Setup & Installation

### Prerequisites

- Python 3.10+
- pip

### Steps

```bash
# 1. Clone / unzip the project
cd movie_recommendation_system

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the app
streamlit run app.py
```

The app will automatically download the TMDB dataset on first launch (~10 MB) and cache it locally.

---

## 8. Usage

1. Open the browser tab that Streamlit launches (default: `http://localhost:8501`).  
2. Use the **sidebar** to choose:
   - Engine type (Content-Based or Hybrid)  
   - Number of recommendations (3–20)  
3. Type or select a movie in the search box.  
4. Click **Find Similar**.  
5. Browse the ranked recommendation cards showing title, year, director, cast, genres, overview, and match percentage.  
6. Optionally download results as CSV or explore the score chart.

---

## 9. Output & Results

### Sample Output (query: *The Dark Knight*)

| Rank | Title | Match % | Rating |
|------|-------|---------|--------|
| 1 | Batman Begins | 94% | 7.6 |
| 2 | The Dark Knight Rises | 91% | 7.8 |
| 3 | Batman v Superman | 78% | 6.0 |
| 4 | Man of Steel | 74% | 6.5 |
| 5 | Watchmen | 71% | 7.3 |

Match % is computed as:  
`score = 0.85 × cosine_sim + 0.15 × (vote_average / 10)`

---

## 10. Future Scope

| Enhancement | Description |
|-------------|-------------|
| **Real CF dataset** | Integrate MovieLens 25M for genuine user-rating collaborative filtering |
| **Deep learning** | BERT-based sentence embeddings for richer semantic similarity |
| **User profiles** | Session-based preference learning; thumbs up/down feedback |
| **Poster images** | Fetch TMDB API poster images for visual cards |
| **Mood filter** | Filter recommendations by mood (e.g., "thriller", "feel-good") |
| **Multilingual** | Support non-English movie databases |
| **Production deploy** | Docker container + cloud deploy (Streamlit Cloud / AWS) |
| **A/B testing** | Evaluate CB vs Hybrid vs deep-learning engines via click-through rate |

---

## 11. References

1. Ricci, F., Rokach, L., & Shapira, B. (2015). *Recommender Systems Handbook*. Springer.  
2. Salton, G., & Buckley, C. (1988). Term-weighting approaches in automatic text retrieval. *Information Processing & Management*.  
3. Scikit-learn documentation — `TfidfVectorizer`, `cosine_similarity`.  
4. TMDB 5000 Movie Dataset — Kaggle.  
5. Streamlit documentation — https://docs.streamlit.io

---

*Built with ❤️ using Python · Pandas · Scikit-learn · Streamlit*
