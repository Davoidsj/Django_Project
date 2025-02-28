from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserDBView, UserStatsView, home_view

router = DefaultRouter()
router.register(r'users', UserDBView, basename='userdb') 
router.register(r'userstats', UserStatsView, basename='userstats')  

urlpatterns = [
    path("", home_view, name="home"),  
    path("api/", include(router.urls)),  # Base API path remains the same
]
