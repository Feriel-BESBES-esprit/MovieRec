# core/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Avg

from core.recommender import get_personalized_recommendations
from .models import Movie, UserRating, WatchlistItem
from django.contrib.auth.models import User

from django.db.models import Q


# core/views.py — REPLACE ONLY THE home function

def home(request):
    # Personalized recommendations (XGBoost) for logged-in users
    recommended_movies = []
    if request.user.is_authenticated:
        recommended_ids = get_personalized_recommendations(request.user.id, n=20)
        recommended_movies = Movie.objects.filter(movie_id__in=recommended_ids)

    # Featured and trending
    all_movies = Movie.objects.all().order_by('-movie_id')[:100]
    featured = all_movies.first() if all_movies.exists() else None

    # Watchlist status
    if request.user.is_authenticated:
        watchlist_ids = set(WatchlistItem.objects.filter(user=request.user).values_list('movie_id', flat=True))
        for movie in all_movies:
            movie.in_watchlist = movie.movie_id in watchlist_ids
    else:
        for movie in all_movies:
            movie.in_watchlist = False

    context = {
        'featured': featured,
        'all_movies': all_movies,
        'recommended_movies': recommended_movies,  # ← Personalized row
        'action_movies': Movie.objects.filter(genres__icontains='Action')[:20],
        'comedy_movies': Movie.objects.filter(genres__icontains='Comedy')[:20],
        'drama_movies': Movie.objects.filter(genres__icontains='Drama')[:20],
        'thriller_movies': Movie.objects.filter(genres__icontains='Thriller')[:20],
        'horror_movies': Movie.objects.filter(genres__icontains='Horror')[:20],
    }
    return render(request, 'core/home.html', context)

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, movie_id=movie_id)

    # User-specific info
    user_rating = None
    in_watchlist = False
    if request.user.is_authenticated:
        user_rating = UserRating.objects.filter(user=request.user, movie=movie).first()
        in_watchlist = WatchlistItem.objects.filter(user=request.user, movie=movie).exists()

    # Average rating
    avg_rating = movie.user_ratings.aggregate(Avg('rating'))['rating__avg']
    rating_count = movie.user_ratings.count()

    # Similar movies (basic genre-based — will replace with cosine later)
    similar_movies = []
    if movie.genres:
        first_genre = movie.genres.split('|')[0].strip()
        similar_movies = Movie.objects.filter(
            genres__icontains=first_genre
        ).exclude(movie_id=movie_id).order_by('-movie_id')[:12]

    context = {
        'movie': movie,
        'user_rating': user_rating,
        'in_watchlist': in_watchlist,
        'average_rating': round(avg_rating, 1) if avg_rating else 0,
        'rating_count': rating_count,
        'similar_movies': similar_movies,
    }
    return render(request, 'core/movie_detail.html', context)

def search(request):
    query = request.GET.get('q', '').strip()
    movies = []
    results_count = 0

    if query:
        movies = Movie.objects.filter(title__icontains=query)[:50]
        results_count = movies.count()

    return render(request, 'core/search.html', {
        'movies': movies,
        'query': query,
        'results_count': results_count
    })


from django.db.models import Prefetch

def browse(request):
    genre = request.GET.get('genre', '').strip()
    
    # Get all movies, filter by genre if provided
    movies = Movie.objects.all()
    if genre:
        movies = movies.filter(genres__icontains=genre)

    # Precompute watchlist for logged-in users
    watchlist_ids = set()
    if request.user.is_authenticated:
        watchlist_ids = set(
            WatchlistItem.objects.filter(user=request.user)
            .values_list('movie_id', flat=True)
        )

    # Add in_watchlist attribute to each movie
    for movie in movies:
        movie.in_watchlist = movie.movie_id in watchlist_ids

    # Extract all unique genres from database
    all_genres = set()
    movies_with_genres = Movie.objects.exclude(genres__isnull=True).exclude(genres='')
    for movie in movies_with_genres:
        genres_list = [g.strip() for g in movie.genres.split('|') if g.strip()]
        all_genres.update(genres_list)
    all_genres = sorted(all_genres)

    context = {
        'movies': movies,
        'genre': genre,
        'all_genres': all_genres,
    }
    return render(request, 'core/browse.html', context)


# core/views.py — REPLACE THESE TWO FUNCTIONS

from django.http import JsonResponse

@login_required
def rate_movie(request, movie_id):
    movie = get_object_or_404(Movie, movie_id=movie_id)
    if request.method == "POST":
        try:
            rating = int(request.POST['rating'])
            if 1 <= rating <= 5:
                UserRating.objects.update_or_create(
                    user=request.user,
                    movie=movie,
                    defaults={'rating': rating}
                )
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success', 'rating': rating})
                messages.success(request, "Rating saved!")
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid rating'}, status=400)
        except:
            return JsonResponse({'status': 'error', 'message': 'Error'}, status=400)
    return redirect('movie_detail', movie_id=movie_id)


@login_required
def toggle_watchlist(request, movie_id):
    movie = get_object_or_404(Movie, movie_id=movie_id)
    obj, created = WatchlistItem.objects.get_or_create(user=request.user, movie=movie)
    added = created
    if not created:
        obj.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'added': added})
    return redirect('movie_detail', movie_id=movie_id)


@login_required
def watchlist(request):
    items = request.user.watchlist.select_related('movie').order_by('-added_at')

    return render(request, 'core/watchlist.html', {
        'watchlist_items': items,
        'watchlist_count': items.count(),
    })



# core/views.py — REPLACE register function
from core.models import UserProfile

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if not all([username, password]):
            messages.error(request, "Please fill required fields!")
            return render(request, 'core/register.html')

        if password != password_confirm:
            messages.error(request, "Passwords do not match!")
            return render(request, 'core/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, 'core/register.html')

        if User.objects.filter(email=email).exists() and email:
            messages.error(request, "Email already in use!")
            return render(request, 'core/register.html')

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Create profile
        profile = UserProfile.objects.create(user=user)
        profile.age = request.POST.get('age', None)
        if profile.age:
            profile.age = int(profile.age)
        profile.gender = request.POST.get('gender', '')
        profile.occupation = int(request.POST.get('occupation', 0)) if request.POST.get('occupation') else None
        profile.zip_code = request.POST.get('zip_code', '')
        profile.save()

        login(request, user)
        messages.success(request, f"Welcome {username}! Your profile is ready for personalized recommendations.")
        return redirect('home')

    return render(request, 'core/register.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Please fill all fields!")
            return render(request, 'core/login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back {username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

# core/views.py — ADD THIS FUNCTION
def more_recommendations(request):
    recommendations = []
    if request.user.is_authenticated:
        recommended_ids = get_personalized_recommendations(request.user.id, n=100)
        recommendations = Movie.objects.filter(movie_id__in=recommended_ids)

    context = {
        'recommendations': recommendations,
        'total': recommendations.count(),
    }
    return render(request, 'core/more_recommendations.html', context)

# core/views.py — ADD THIS FUNCTION
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg
from core.models import Movie, UserRating, UserProfile
import pandas as pd
import json

# core/views.py — REPLACE THE admin_dashboard FUNCTION WITH THIS

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg
from core.models import Movie, UserRating
from django.contrib.auth.models import User
import os
import pickle
from django.conf import settings
import json

# core/views.py — FINAL PROFESSIONAL VERSION

@staff_member_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_movies = Movie.objects.count()
    total_ratings = UserRating.objects.count()
    avg_ratings_per_user = round(total_ratings / total_users if total_users else 0, 2)

    popular_movies = Movie.objects.annotate(
        rating_count=Count('user_ratings'),
        avg_rating=Avg('user_ratings__rating')
    ).order_by('-rating_count')[:10]

    genre_stats = []
    genres = ['Action', 'Comedy', 'Drama', 'Thriller', 'Horror', 'Romance', 'Sci-Fi', 'Adventure']
    for genre in genres:
        count = Movie.objects.filter(genres__icontains=genre).count()
        genre_stats.append({'genre': genre, 'count': count})

    # LOAD YOUR REAL ML CLUSTERING (list of Series)
    segment_data = []
    clustering_info = {'k': 'N/A', 'silhouette': 'N/A', 'balance': 'N/A'}
    cluster_genres = []

    try:
        cluster_profiles = pickle.load(open(os.path.join(settings.BASE_DIR, 'data', 'cluster_profiles.pkl'), 'rb'))
        best_k = len(cluster_profiles)  # number of clusters = length of list
        best_config = pickle.load(open(os.path.join(settings.BASE_DIR, 'data', 'best_config.pkl'), 'rb'))

        # Approximate cluster sizes (from your earlier output)
        cluster_sizes = [148, 203, 149]  # from your print: 148, 203, 149
        total = sum(cluster_sizes)
        percentages = [round(s / total * 100, 1) for s in cluster_sizes]

        # Build segment data and genre preferences
        for i, series in enumerate(cluster_profiles):
            preferences = series.to_dict()
            top_genre = max(preferences, key=preferences.get)
            top_score = round(preferences[top_genre], 3)

            segment_data.append({
                'segment': f"Cluster {i}",
                'count': cluster_sizes[i],
                'percentage': percentages[i]
            })

            cluster_genres.append({
                'cluster': i,
                'top_genre': top_genre,
                'top_score': top_score,
                'preferences': {g: round(preferences.get(g, 0), 3) for g in genres}
            })

        clustering_info = {
            'k': best_k,
            'silhouette': round(best_config.get('Silhouette', 0), 4),
            'balance': round(best_config.get('Balance_Ratio', 0), 4)
        }
    except Exception as e:
        print("Clustering load error:", e)
        segment_data = []
        cluster_genres = []

    context = {
        'total_users': total_users,
        'total_movies': total_movies,
        'total_ratings': total_ratings,
        'avg_ratings_per_user': avg_ratings_per_user,
        'popular_movies': popular_movies,
        'genre_stats': json.dumps(genre_stats),
        'segment_data': json.dumps(segment_data),
        'clustering_info': clustering_info,
        'cluster_genres': cluster_genres,  # NEW: real genre preferences
    }
    return render(request, 'core/admin_dashboard.html', context)
