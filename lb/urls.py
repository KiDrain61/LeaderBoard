from django.urls import path, include
from . import views

urlpatterns = [
    # TODO: Config URL Patterns
    path('leaderboard', views.leaderboard),
    path("history/<slug:qusername>", views.history),
    path("submit", views.submit),
    path("vote", views.vote),
]
