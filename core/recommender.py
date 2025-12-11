# core/recommender.py
import pickle
import numpy as np
from django.conf import settings
import os

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
def get_personalized_recommendations(user_id, n=15):
    if user_id not in data['UserID'].values:
        # Cold start
        popular = data.groupby('MovieID')['Rating'].agg(['mean', 'count'])
        popular = popular[popular['mean'] > 4.2].sort_values('count', ascending=False).head(n)
        return popular.index.tolist()

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

# Similar movies for detail page
def get_similar_movies(movie_id, n=10):
    try:
        idx = movies_sim[movies_sim['MovieID'] == movie_id].index[0]
        distances = similarity_matrix.iloc[idx]
        similar_indices = distances.nlargest(n+1).index[1:]  # skip itself
        return movies_sim.iloc[similar_indices]['MovieID'].tolist()
    except:
        return []