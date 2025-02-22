from django.db import models

class UserDB(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    imgurl = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'usersdb'


class UserStats(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    watch = models.IntegerField(default=0)

    class Meta:
        db_table = 'userstats'

