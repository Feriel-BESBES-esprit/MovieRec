# core/recommender.py
import pickle
import numpy as np
from django.conf import settings
import os
from django.db.models import Avg

# Load models once when Django starts
DATA_PATH = os.path.join(settings.BASE_DIR, 'data', 'data.pkl')
XGB_PATH = os.path.join(settings.BASE_DIR, 'data', 'xgb_model.pkl')
CLUSTER_SIM_PATH = os.path.join(settings.BASE_DIR, 'data', 'cluster_sim.pkl')
MOVIES_SIM_PATH = os.path.join(settings.BASE_DIR, 'data', 'movies_for_similarity.pkl')
SIM_MATRIX_PATH = os.path.join(settings.BASE_DIR, 'data', 'similarity_matrix.pkl')

data = pickle.load(open(DATA_PATH, 'rb'))
xgb_model = pickle.load(open(XGB_PATH, 'rb'))
cluster_sim = pickle.load(open(CLUSTER_SIM_PATH, 'rb'))
movies_sim = pickle.load(open(MOVIES_SIM_PATH, 'rb'))
similarity_matrix = pickle.load(open(SIM_MATRIX_PATH, 'rb'))

# Personalized recommendations (your XGBoost)
# core/recommender.py — REPLACE WITH THIS

def get_personalized_recommendations(user_id, n=15):
    from core.models import UserRating, Movie, UserProfile

    # Try original MovieLens logic (for loaded users)
    if user_id in data['UserID'].values:
        # Your EXACT notebook logic
        user_data = data[data['UserID'] == user_id].iloc[0]
        user_cluster = int(user_data['cluster'])
        rated = set(data[data['UserID'] == user_id]['MovieID'])
        candidates = data[~data['MovieID'].isin(rated)]['MovieID'].unique()[:500]

        preds = []
        for mid in candidates:
            m = data[data['MovieID'] == mid].iloc[0]
            feat = np.array([
                user_data['Age'], 1 if user_data['Gender'] == 'M' else 0,
                user_data['Occupation'], user_data['user_total_ratings'],
                user_data['user_avg_rating'], user_data['user_std_rating'] or 0,
                m['movie_popularity'], m['Year'], m['GenreCount'],
                m['Comedy'], m['Drama'], m['Action'], m['Sci-Fi'],
                m['Thriller'], m['Romance'], m['Adventure'], m['Crime']
            ]).reshape(1, -1)

            prob = xgb_model.predict_proba(feat)[0, 1]
            boost = 1.0 + 0.4 * cluster_sim[user_cluster].mean()
            score = prob * boost
            preds.append((mid, score))

        preds.sort(key=lambda x: x[1], reverse=True)
        return [mid for mid, _ in preds[:n]]

    # NEW USER — Use real-time features from Django
    try:
        profile = UserProfile.objects.get(user_id=user_id)
        user_ratings = UserRating.objects.filter(user_id=user_id)
        
        total_ratings = user_ratings.count()
        avg_rating = user_ratings.aggregate(Avg('rating'))['rating__avg'] or 3.0
        ratings_list = list(user_ratings.values_list('rating', flat=True))
        std_rating = np.std(ratings_list) if ratings_list else 0

        # Default values if missing
        age = profile.age or 30
        gender_m = 1 if profile.gender == 'M' else 0
        occupation = profile.occupation or 0

        # Approximate cluster (simple: high rater = cluster 1)
        user_cluster = 1 if avg_rating > 4.0 else 0

        rated_ids = set(user_ratings.values_list('movie_id', flat=True))
        candidates = Movie.objects.exclude(movie_id__in=rated_ids)[:500]

        preds = []
        for movie in candidates:
            feat = np.array([
                age, gender_m, occupation,
                total_ratings, avg_rating, std_rating,
                getattr(movie, 'movie_popularity', 0) or 0,
                movie.year or 2000,
                len(movie.genres.split('|')) if movie.genres else 1,
                1 if 'Comedy' in movie.genres else 0,
                1 if 'Drama' in movie.genres else 0,
                1 if 'Action' in movie.genres else 0,
                1 if 'Sci-Fi' in movie.genres else 0,
                1 if 'Thriller' in movie.genres else 0,
                1 if 'Romance' in movie.genres else 0,
                1 if 'Adventure' in movie.genres else 0,
                1 if 'Crime' in movie.genres else 0,
            ]).reshape(1, -1)

            prob = xgb_model.predict_proba(feat)[0, 1]
            boost = 1.0 + 0.4 * cluster_sim[user_cluster].mean()
            score = prob * boost
            preds.append((movie.movie_id, score))

        preds.sort(key=lambda x: x[1], reverse=True)
        return [mid for mid, _ in preds[:n]]

    except UserProfile.DoesNotExist:
        pass

    # Final fallback
    return Movie.objects.order_by('-movie_id')[:n]
# Similar movies for detail page


def get_similar_movies(movie_id, n=10):
    try:
        idx = movies_sim[movies_sim['MovieID'] == movie_id].index[0]
        distances = similarity_matrix.iloc[idx]
        similar_indices = distances.nlargest(n+1).index[1:]  # skip itself
        return movies_sim.iloc[similar_indices]['MovieID'].tolist()
    except:
        return []