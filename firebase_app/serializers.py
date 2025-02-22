from rest_framework import serializers
from .models import UserDB, UserStats

class UserDBSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDB
        fields = ['id', 'name', 'imgurl', 'email']

class UserStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStats
        fields = ['id', 'likes', 'dislikes', 'watch']
