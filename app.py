"""Flask application for mood-aware movie discovery."""
import os
import re
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Environment variables can also be supplied by the shell or deployment.
    pass
from services.emotion_detector import detect_emotion, detect_desired_experience
from services.mood_engine import build_mood_plan, EMOTIONS, FRIENDSHIP, RELATIONSHIPS, GROWTH, GENRES, SITUATIONS
from services.recommender import MovieRecommender, explain
from services.movie_api import attach_posters

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "local-development-key")
app.config["SESSION_COOKIE_SECURE"] = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
recommender = MovieRecommender()

@app.get("/")
def index():
    genres = sorted({g for value in recommender.movies["genres"] for g in str(value).split("|") if g})
    return render_template("index.html", genres=genres, categories={"Emotions": [x.title() for x in EMOTIONS], "Friendship": FRIENDSHIP, "Love and Relationships": RELATIONSHIPS, "Motivation": GROWTH, "Life Situations": SITUATIONS, "Entertainment": GENRES, "Comfort Movies": ("Comfort Movies", "Feel-Good Movies", "Light-Hearted Movies", "Need a Good Laugh", "Need to Relax")})

@app.get("/privacy")
def privacy():
    return render_template("privacy.html")

@app.get("/terms")
def terms():
    return render_template("terms.html")

@app.post("/recommend")
def recommend():
    text = request.form.get("mood_text", "").strip()
    mood = (request.form.get("mood", "").strip().lower() or detect_emotion(text))
    experience = request.form.get("experience", "").strip().lower() or detect_desired_experience(text, mood)
    if not text and not mood and not experience:
        flash("Tell us a little about how you feel, or pick a mood to continue.", "error")
        return redirect(url_for("index"))
    plan = build_mood_plan(mood, experience) if mood or experience else None
    if plan is None:
        flash("We couldn't quite identify that mood. Try a mood like calm, sad, excited or stressed.", "error")
        return redirect(url_for("index"))
    prefs = {"favorite_genres": request.form.get("favorite_genres", ""), "min_rating": request.form.get("preference_rating", "0"), "actors": request.form.get("actors", ""), "directors": request.form.get("directors", "")}
    movies = recommender.recommend(plan, limit=12, preferences=prefs, genre=request.form.get("genre", ""), theme=request.form.get("theme", ""), min_rating=request.form.get("min_rating", 0), year_from=request.form.get("year_from", 0), year_to=request.form.get("year_to", 0), language=request.form.get("language", ""), min_runtime=request.form.get("min_runtime", 0), max_runtime=request.form.get("max_runtime", 0), min_popularity=request.form.get("min_popularity", 0), emotional_tone=request.form.get("emotional_tone", ""))
    for movie in movies:
        movie["why"] = explain(movie, plan)
    attach_posters(movies)
    if not movies:
        flash("We couldn't find a match with those filters. Try lowering the rating or removing a filter.", "error")
        return redirect(url_for("index"))
    return render_template("results.html", movies=movies, mood=plan.mood, plan=plan, genre=request.form.get("genre", ""), min_rating=request.form.get("min_rating", ""), year_from=request.form.get("year_from", ""))

@app.get("/api/recommend")
def api_recommend():
    text = request.args.get("q", "")
    mood = request.args.get("mood", "").lower() or detect_emotion(text)
    experience = request.args.get("experience", "").lower() or detect_desired_experience(text, mood)
    plan = build_mood_plan(mood or "", experience)
    if not plan:
        return jsonify({"error": "Please describe a supported mood."}), 400
    try:
        limit = max(1, min(int(request.args.get("limit", 9)), 30))
    except (TypeError, ValueError):
        limit = 9
    movies = recommender.recommend(plan, limit=limit, genre=request.args.get("genre", ""), theme=request.args.get("theme", ""), min_rating=request.args.get("min_rating", 0), language=request.args.get("language", ""), year_from=request.args.get("year_from", 0), year_to=request.args.get("year_to", 0), min_runtime=request.args.get("min_runtime", 0), max_runtime=request.args.get("max_runtime", 0), min_popularity=request.args.get("min_popularity", 0), emotional_tone=request.args.get("emotional_tone", ""))
    for movie in movies:
        movie["why"] = explain(movie, plan)
    attach_posters(movies)
    return jsonify({"mood": mood, "experience": experience, "goal": plan.goal, "movies": movies})

def search_catalog(query, limit=18):
    query = (query or "").strip()
    if not query:
        return []
    haystack = (recommender.movies["title"] + " " + recommender.movies["overview"] + " " + recommender.movies["genres"].str.replace("|", " ", regex=False)).str.lower()
    matches = recommender.movies[haystack.str.contains(query.lower(), regex=False)].copy()
    matches["match_score"] = matches["title"].str.lower().apply(lambda title: 1.0 if title == query.lower() else (0.8 if query.lower() in title else 0.35))
    movies = matches.sort_values(["match_score", "rating", "popularity"], ascending=False).head(limit).to_dict("records")
    for movie in movies:
        movie["why"] = "This title matched your movie search."
    return attach_posters(movies)

@app.get("/search")
def search_movies():
    query = request.args.get("q", "").strip()
    movies = search_catalog(query)
    return render_template("search_results.html", movies=movies, query=query)

@app.get("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Enter a movie title to search."}), 400
    return jsonify({"query": query, "movies": search_catalog(query)})

@app.get("/health")
def health():
    return jsonify({"status": "ok", "movies": len(recommender.movies)})

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
