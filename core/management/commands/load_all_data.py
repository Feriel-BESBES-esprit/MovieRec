# core/management/commands/load_all_data.py
import pandas as pd
import requests
import time
from django.core.management.base import BaseCommand
from core.models import Movie, UserProfile
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Load all data + download real movie posters from TMDB"

    def handle(self, *args, **options):
        TMDB_KEY = "1bd56defba4e0c8f0fb0f41969a86a89"  # Get free at: https://www.themoviedb.org/settings/api
        IMG_BASE = "https://image.tmdb.org/t/p/w500"

        # === 1. Load Movies + Download Posters ===
        self.stdout.write("Loading movies + posters...")
        df = pd.read_csv("data/movies_clean.csv")

        for idx, row in df.iterrows():
            movie_id = int(row['MovieID'])
            title_raw = str(row['Title']) if pd.notna(row['Title']) else "Unknown"
            title = title_raw.split(' (')[0].strip('"')
            year = None
            import re
            match = re.search(r'\((\d{4})\)', title_raw)
            if match:
                year = int(match.group(1))

            movie, created = Movie.objects.update_or_create(
                movie_id=movie_id,
                defaults={'title': title_raw, 'genres': row['Genres'] if pd.notna(row['Genres']) else ""}
            )

            # Download poster if missing
            if not movie.poster_url and TMDB_KEY != "YOUR_TMDB_KEY":
                try:
                    url = f"https://api.themoviedb.org/3/search/movie"
                    params = {'api_key': TMDB_KEY, 'query': title, 'year': year}
                    r = requests.get(url, params=params, timeout=10)
                    data = r.json()
                    if data['results']:
                        path = data['results'][0].get('poster_path')
                        if path:
                            movie.poster_url = IMG_BASE + path
                            movie.save()
                            self.stdout.write(f"Poster: {title}")
                except:
                    pass
                time.sleep(0.05)  # Be nice to TMDB

            if (idx + 1) % 50 == 0:
                self.stdout.write(f"Processed {idx + 1}/{len(df)} movies...")

        # === 2. Load Users ===
              # === 2. Load Users with full profile ===
        self.stdout.write("Loading users with profiles...")
        users_df = pd.read_csv("data/users_clean.csv")
        
        for _, row in users_df.iterrows():
            user_id = int(row['UserID'])
            username = f"user{user_id}"
            email = f"{username}@gmail.com"
            
            # Create or update user
            user, created = User.objects.update_or_create(
                id=user_id,
                defaults={
                    'username': username,
                    'email': email,
                }
            )
            
            # Set password
            if created or not user.has_usable_password():
                user.set_password('A123456789$')
                user.save()
            
            # Create or update profile
            profile, _ = UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'age': int(row['Age']) if pd.notna(row['Age']) else None,
                    'gender': row['Gender'],
                    'occupation': int(row['Occupation']),
                    'zip_code': str(row['Zip-code']),
                }
            )
            
            if (user_id % 500 == 0):
                self.stdout.write(f"Processed {user_id} users...")

        # === 3. Load Ratings ===
        self.stdout.write("Loading 1M+ ratings...")
        from core.models import UserRating
        UserRating.objects.all().delete()
        ratings_df = pd.read_csv("data/ratings_clean.csv")
        batch = []
        for _, row in ratings_df.iterrows():
            batch.append(UserRating(
                user_id=int(row['UserID']),
                movie_id=int(row['MovieID']),
                rating=int(row['Rating'])
            ))
            if len(batch) >= 1000:
                UserRating.objects.bulk_create(batch, ignore_conflicts=True)
                batch = []
        if batch:
            UserRating.objects.bulk_create(batch, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS("EVERYTHING LOADED + POSTERS DOWNLOADED!"))