# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('movie/<str:movie_id>/', views.movie_detail, name='movie_detail'),
    path('search/', views.search, name='search'),
    path('browse/', views.browse, name='browse'),
    path('watchlist/', views.watchlist, name='watchlist'),
    
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # AJAX actions
    path('rate/<int:movie_id>/', views.rate_movie, name='rate_movie'),
    path('watchlist/toggle/<int:movie_id>/', views.toggle_watchlist, name='toggle_watchlist'),

]