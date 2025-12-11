# core/models.py
from django.db import models
from django.contrib.auth.models import User
import re

class Movie(models.Model):
    movie_id = models.IntegerField(primary_key=True)  # MovieID from CSV
    title = models.CharField(max_length=500)
    genres = models.TextField(blank=True, null=True)
    year = models.IntegerField(null=True, blank=True)
    poster_url = models.URLField(blank=True, null=True)

    class Meta:
        db_table = 'core_movie'

    def __str__(self):
        return self.title

    def clean_title(self):
        return re.sub(r'\s*\(\d{4}\)', '', self.title).strip('"')

    def get_year(self):
        match = re.search(r'\((\d{4})\)', self.title)
        return int(match.group(1)) if match else None

    def save(self, *args, **kwargs):
        if self.year is None:
            self.year = self.get_year()
        super().save(*args, **kwargs)


class UserRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='user_ratings')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'movie']

    def __str__(self):
        return f"{self.user.username} → {self.movie}: {self.rating}/5"


class WatchlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    watched = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'movie']